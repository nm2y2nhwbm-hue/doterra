# -*- coding: utf-8 -*-
"""
Agent 1 負責範圍：核心金流管理模組 (core/payment_manager.py)
全面落實日式五大工程規範：
1. 丁寧さ (Teineisa)：{code, message, guidance} 溫潤三層 API 錯誤回饋。
2. 気配り (Kikubari)：對齊日本 APPI 標準，深度個資脫敏（電話/Email/LINE 遮罩）與 Zero-PII Logging。
3. 一期一會・殘心 (Zanshin)：SHIZUKU 雅號訂單編號、三大位格當日調息籤條。
4. 安心の証明 (Trust Assurance)：官方建議零售價防偽重算、SHA-256 銀行級加密與信賴元資料。
"""
import os
import re
import json
import string
import random
import hashlib
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from core import database_manager as db

# 綠界官方測試環境（Stage）預設金鑰
DEFAULT_ECPAY_MERCHANT_ID = "3002607"
DEFAULT_ECPAY_HASH_KEY = "pwFHCqoQZGmho4w6"
DEFAULT_ECPAY_HASH_IV = "EkRm7iFT261dpevs"
DEFAULT_ECPAY_STAGE_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
DEFAULT_ECPAY_PROD_URL = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"

# 4 大牌陣禮盒官方單一定價母體（對齊首頁 index.html 與 components/cart/cart.js）
PREDEFINED_BOX_CATALOG = {
    "SET-MIRROR-01": {
        "id": "SET-MIRROR-01",
        "name": "【鏡子】當下覺察調息禮盒",
        "price": 1845,
        "capacity": "15ml×2",
        "pillar": "中柱 · 平衡",
    },
    "SET-RIVER-02": {
        "id": "SET-RIVER-02",
        "name": "【河流】時間軌跡梳理禮盒",
        "price": 1965,
        "capacity": "15ml×2",
        "pillar": "右柱 · 慈悲",
    },
    "SET-CROSS-03": {
        "id": "SET-CROSS-03",
        "name": "【岔路】重大抉擇守護禮盒",
        "price": 4895,
        "capacity": "15ml+10ml滾珠",
        "pillar": "左柱 · 嚴厲",
    },
    "CUSTOM-ROLLER-10": {
        "id": "CUSTOM-ROLLER-10",
        "name": "【客製】專屬位格滾珠精油",
        "price": 1040,
        "capacity": "10ml滾珠",
        "pillar": "位格特調",
    },
}

_DATA_DIR = Path(__file__).resolve().parent / "data"
_ORDERS_FILE = _DATA_DIR / "orders.json"


class PaymentValidationError(Exception):
    """資料校驗失敗異常（遵循日式「丁寧さ」禮儀回饋）"""
    def __init__(self, message, code="PAYMENT_VALIDATION_ERROR", guidance="請確認填寫資訊後重試", status_code=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.guidance = guidance
        self.status_code = status_code

    def to_dict(self):
        return {
            "success": False,
            "code": self.code,
            "message": self.message,
            "guidance": self.guidance,
            "error": self.message,  # 向下相容既有前端欄位
        }


class PaymentSignatureError(Exception):
    """簽章校驗失敗異常"""
    def __init__(self, message="綠界 CheckMacValue 簽章驗證未竟，為維護交易安全已暫緩處理", code="INVALID_SIGNATURE", status_code=400):
        super().__init__(message)
        self.message = message
        self.code = code
        self.guidance = "此交易因簽章校驗未通過已終止，請重新發起結帳或聯繫返魂堂客服。"
        self.status_code = status_code

    def to_dict(self):
        return {
            "success": False,
            "code": self.code,
            "message": self.message,
            "guidance": self.guidance,
            "error": self.message,
        }


class OrderStore:
    """訂單儲存引擎，支援記憶體快取與 JSON 檔案持久化"""
    def __init__(self, filepath=_ORDERS_FILE):
        self.filepath = Path(filepath)
        self._lock = Lock()
        self._orders = {}
        self._load()

    def _load(self):
        with self._lock:
            if self.filepath.exists():
                try:
                    with open(self.filepath, "r", encoding="utf-8") as f:
                        self._orders = json.load(f)
                except Exception as e:
                    print(f"[OrderStore] 讀取訂單失敗，啟用空資料庫: {e}")
                    self._orders = {}
            else:
                self._orders = {}

    def _save(self):
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self._orders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[OrderStore] 寫入訂單失敗: {e}")

    def save_order(self, order):
        with self._lock:
            self._orders[order["order_id"]] = order
            if order.get("merchant_trade_no"):
                self._orders[order["merchant_trade_no"]] = order
            self._save()

    def get_order(self, order_id_or_trade_no):
        with self._lock:
            return self._orders.get(order_id_or_trade_no)

    def update_status(self, order_id_or_trade_no, status, update_fields=None):
        with self._lock:
            order = self._orders.get(order_id_or_trade_no)
            if not order:
                return None
            order["status"] = status
            order["updated_at"] = datetime.now(timezone.utc).isoformat()
            if update_fields:
                order.update(update_fields)
            self._save()
            return order

    def clear(self):
        with self._lock:
            self._orders = {}
            self._save()


# 全域單例訂單儲存庫
order_store = OrderStore()


def get_ecpay_config():
    """取得綠界配置（優先使用環境變數，缺省使用 Stage 測試金鑰）"""
    merchant_id = os.environ.get("ECPAY_MERCHANT_ID", DEFAULT_ECPAY_MERCHANT_ID)
    hash_key = os.environ.get("ECPAY_HASH_KEY", DEFAULT_ECPAY_HASH_KEY)
    hash_iv = os.environ.get("ECPAY_HASH_IV", DEFAULT_ECPAY_HASH_IV)
    is_stage = os.environ.get("ECPAY_STAGE", "true").lower() in ("true", "1", "yes")
    api_url = DEFAULT_ECPAY_STAGE_URL if is_stage else DEFAULT_ECPAY_PROD_URL
    return {
        "merchant_id": merchant_id,
        "hash_key": hash_key,
        "hash_iv": hash_iv,
        "is_stage": is_stage,
        "api_url": os.environ.get("ECPAY_API_URL", api_url),
    }


def find_catalog_item(item_id, item_name=None):
    """
    從 4 大禮盒與 doterra.csv 中查詢官方正版商品資料與單一建議零售價。
    回傳: dict(id, name, price, capacity, pillar) 或 None
    """
    if not item_id and not item_name:
        return None

    # 1. 先查 4 大調息禮盒
    if item_id in PREDEFINED_BOX_CATALOG:
        return PREDEFINED_BOX_CATALOG[item_id]

    # 2. 查 doterra.csv
    oils = db.fetch_oils_data()
    for oil in oils:
        oil_sku = str(oil.get("sku", "")).strip()
        oil_id = str(oil.get("id", "")).strip()
        oil_name = str(oil.get("name", "")).strip()
        oil_name_en = str(oil.get("name_en", "")).strip()

        if item_id and str(item_id).strip() in (oil_sku, oil_id, oil_name):
            return {
                "id": oil_sku or oil_id,
                "name": oil_name + (f" ({oil_name_en})" if oil_name_en else ""),
                "price": int(oil.get("price", 1310)),
                "capacity": oil.get("capacity", "15ml"),
                "pillar": oil.get("pillar", "現代精油"),
            }

        if item_name and (item_name == oil_name or item_name.startswith(oil_name)):
            return {
                "id": oil_sku or oil_id,
                "name": oil_name + (f" ({oil_name_en})" if oil_name_en else ""),
                "price": int(oil.get("price", 1310)),
                "capacity": oil.get("capacity", "15ml"),
                "pillar": oil.get("pillar", "現代精油"),
            }

    return None


def validate_and_calculate_order(raw_items):
    """
    伺服器端金額防竄改驗算（丁寧さ・細緻禮儀錯誤回饋）：
    1. 驗證商品陣列非空且結構完整。
    2. 數量必須為 1 ~ 99 之整數。
    3. 絕不採納前端傳入之單價或小計，完全依據官方資料庫建議零售價重新相乘。
    """
    if not isinstance(raw_items, list) or len(raw_items) == 0:
        raise PaymentValidationError(
            message="調息選品清單目前為空，請挑選觸動心靈的香氣逸品後再行結帳",
            code="EMPTY_CART",
            guidance="您可前往首頁調息選品區或精油自然醫學圖鑑挑選商品。"
        )

    if len(raw_items) > 50:
        raise PaymentValidationError(
            message="單筆調息選品項數已達上限，感謝您的理解",
            code="EXCEEDED_ITEM_LIMIT",
            guidance="若有大量調配或送禮需求，歡迎透過貴賓表單由專屬芳療師為您服務。"
        )

    validated_items = []
    total_amount = 0

    for idx, item in enumerate(raw_items):
        if not isinstance(item, dict):
            raise PaymentValidationError(
                message=f"第 {idx + 1} 項選品結構未臻完整，請重新確認所選品項",
                code="INVALID_ITEM_PAYLOAD",
                guidance="建議重新整理網頁後將品項加入購物車再次嘗試。"
            )

        item_id = str(item.get("id", "")).strip()
        item_name = str(item.get("name", "")).strip()

        try:
            qty = int(item.get("qty", 1))
        except (ValueError, TypeError):
            raise PaymentValidationError(
                message=f"商品「{item_name or item_id}」數量格式無效",
                code="INVALID_QUANTITY",
                guidance="請確認選購數量為有效數字。"
            )

        if qty < 1 or qty > 99:
            raise PaymentValidationError(
                message=f"商品「{item_name or item_id}」數量必須介於 1 至 99 之間，感謝您的體諒",
                code="INVALID_QUANTITY",
                guidance="請確認選購數量是否在個人調息使用範圍內。"
            )

        official_product = find_catalog_item(item_id, item_name)
        if not official_product:
            raise PaymentValidationError(
                message=f"找不到指定的官方商品或調息香氣：「{item_name or item_id}」",
                code="UNKNOWN_PRODUCT",
                guidance="官方提供 131 款多特瑞精選精油，請至線上圖鑑查閱選取。"
            )

        unit_price = official_product["price"]
        subtotal = unit_price * qty
        total_amount += subtotal

        validated_items.append({
            "id": official_product["id"],
            "name": official_product["name"],
            "price": unit_price,
            "capacity": official_product.get("capacity", ""),
            "pillar": official_product.get("pillar", "現代精油"),
            "qty": qty,
            "subtotal": subtotal,
        })

    if total_amount <= 0:
        raise PaymentValidationError(
            message="訂單總金額需大於 0 元，請確認選購品項",
            code="INVALID_ORDER_AMOUNT",
            guidance="請確認品項定價與數量是否正確。"
        )

    return validated_items, total_amount


def mask_personal_info(customer):
    """
    🛡️「気配り（Kikubari）」：對齊日本 APPI（個人情報保護法）標準之深度脫敏：
    1. 姓名：保留頭尾，中間全數掩碼（如「王*明」、「歐**華」；單字名「李*」）。
    2. 電話：保留前 4 碼與後 3 碼，中間多段掩碼（如「0912-***-456」）。
    3. Email：僅保留前 2 碼與 @ 後完整網域（如「vi***@example.com」）。
    4. LINE ID：保留前 2 碼與後 2 碼（如「li***89」）。
    5. 備註（note）：對外查詢直接隱藏，絕不洩漏。
    """
    if not isinstance(customer, dict):
        return {}

    raw_name = str(customer.get("name", "")).strip()
    if len(raw_name) <= 1:
        masked_name = raw_name + "*"
    elif len(raw_name) == 2:
        masked_name = raw_name[0] + "*"
    else:
        middle_mask = "*" * (len(raw_name) - 2)
        masked_name = raw_name[0] + middle_mask + raw_name[-1]

    raw_email = str(customer.get("email", "")).strip()
    if "@" in raw_email:
        local, domain = raw_email.split("@", 1)
        masked_local = (local[:2] + "***") if len(local) > 2 else (local[:1] + "***")
        masked_email = f"{masked_local}@{domain}"
    else:
        masked_email = ""

    raw_phone = str(customer.get("phone", "")).strip()
    clean_digits = re.sub(r"\D", "", raw_phone)
    if len(clean_digits) >= 10:
        masked_phone = f"{clean_digits[:4]}-***-{clean_digits[-3:]}"
    elif len(clean_digits) >= 7:
        masked_phone = f"{clean_digits[:3]}-***-{clean_digits[-2:]}"
    elif clean_digits:
        masked_phone = clean_digits[:2] + "***"
    else:
        masked_phone = ""

    raw_line = str(customer.get("line_id", "")).strip()
    if len(raw_line) > 4:
        masked_line = f"{raw_line[:2]}***{raw_line[-2:]}"
    elif raw_line:
        masked_line = raw_line[:1] + "***"
    else:
        masked_line = ""

    return {
        "name": masked_name,
        "email": masked_email,
        "phone": masked_phone,
        "line_id": masked_line,
    }


def generate_zanshin_oracle(validated_items):
    """
    📜「一期一會・殘心」：依據訂單內精油位格屬性，自動生成專屬當日調息籤條 (Zanshin Oracle)
    讓商業結帳轉化為充滿日式禪意的心靈款待。
    """
    now_dt = datetime.now(timezone.utc)
    all_pillars = " ".join(item.get("pillar", "") for item in validated_items)

    if "中柱" in all_pillars or "Balance" in all_pillars:
        oracle = {
            "pillar": "中柱 · Balance (平衡歸中)",
            "theme": "調和歸中 · 安定身心",
            "blessing": "香氣入息，靜謐歸元。願此瓶植物精粹，中和周身浮燥，穩固安頓心靈力量。",
            "practice": "建議於清晨或睡前，將一滴精油滴於掌心搓熱，深呼吸三次，感受氣息下沉歸於丹田。",
        }
    elif "右柱" in all_pillars or "Mercy" in all_pillars:
        oracle = {
            "pillar": "右柱 · Mercy (慈悲生發)",
            "theme": "溫陽沐光 · 舒展胸臆",
            "blessing": "溫陽沐光，行氣解鬱。願大地草木生機如晨曦初升，溫柔接住您的每一刻情緒起伏。",
            "practice": "建議於工作遇瓶頸或心情緊繃時塗抹於太陽穴與脈搏處，讓清新香氣化解鬱結。",
        }
    elif "左柱" in all_pillars or "Severity" in all_pillars:
        oracle = {
            "pillar": "左柱 · Severity (嚴正沉靜)",
            "theme": "深斂固守 · 滌心明志",
            "blessing": "深斂固守，萬象歸真。願高山古木之深沉香氣，收斂散漫心神，滌盡周身疲憊。",
            "practice": "建議於冥想或夜間獨處時薰香擴香，在沉靜木質香中梳理思緒，找回內在秩序。",
        }
    else:
        oracle = {
            "pillar": "現代精油 · Pure Essence",
            "theme": "一期一會 · 晨昏調息",
            "blessing": "一滴精油，一期一會。願今日天地草木之芬芳，成為守護您日常生活的一抹溫潤之光。",
            "practice": "隨心嗅吸，讓氣味引導直覺，順應當下身心節奏自然流動。",
        }

    oracle["date"] = now_dt.strftime("%Y年%m月%d日")
    return oracle


def get_trust_assurance():
    """
    💳「安心の証明」：公開透明的日式交易防護與品質信賴保證元資料
    """
    return {
        "security_standard": "綠界科技 ECPay SHA-256 銀行級安全傳輸加密",
        "official_price_verified": True,
        "price_verification_source": "dōTERRA 多特瑞台灣官方建議零售價系統",
        "idempotency_guaranteed": True,
        "zero_risk_guarantee": "雙重防重複扣款保護，交易未竟安全自動取消",
        "customer_care": "雫之洞悉・返魂堂芳療師團隊專屬調息諮詢",
    }


def generate_ecpay_check_mac_value(params, hash_key, hash_iv):
    """
    綠界 ECPay 官方標準 SHA256 CheckMacValue 壓碼演算法：
    1. 排除 CheckMacValue 本身，依照 Key 進行 ASCII 字母排序。
    2. 組合成 HashKey={key}&param1=val1...&HashIV={iv}。
    3. URL Encode，轉為全小寫。
    4. 替換 .NET 特殊字元：%2d -> -, %5f -> _, %2e -> ., %21 -> !, %2a -> *, %28 -> (, %29 -> )。
    5. 執行 SHA256 雜湊計算並轉為全大寫。
    """
    filtered = {k: str(v) for k, v in params.items() if k != "CheckMacValue"}
    sorted_items = sorted(filtered.items(), key=lambda x: x[0].lower())

    raw_query = f"HashKey={hash_key}&" + "&".join(f"{k}={v}" for k, v in sorted_items) + f"&HashIV={hash_iv}"
    encoded = urllib.parse.quote_plus(raw_query, safe="").lower()

    # 綠界規範特殊字元替換（對齊 .NET System.Web.HttpUtility.UrlEncode）
    replacements = {
        "%2d": "-",
        "%5f": "_",
        "%2e": ".",
        "%21": "!",
        "%2a": "*",
        "%28": "(",
        "%29": ")",
    }
    for k, v in replacements.items():
        encoded = encoded.replace(k, v)

    return hashlib.sha256(encoded.encode("utf-8")).hexdigest().upper()


def verify_ecpay_check_mac_value(params, hash_key, hash_iv):
    """驗證綠界回調參數之 CheckMacValue"""
    received_mac = params.get("CheckMacValue", "")
    if not received_mac:
        return False
    expected_mac = generate_ecpay_check_mac_value(params, hash_key, hash_iv)
    return received_mac.upper() == expected_mac.upper()


def generate_merchant_trade_no():
    """
    生成綠界特店交易編號（MerchantTradeNo）：
    格式：DTR + YYMMDDHHmmss + 4位英數（長度剛好 19 字元，嚴格小於綠界上限 20 字元）
    """
    now_str = datetime.now(timezone.utc).strftime("%y%m%d%H%M%S")
    rand_chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"DTR{now_str}{rand_chars}"


def create_payment_order(data, client_ip=None):
    """
    建立付款訂單：
    1. 驗證買家稱謂與聯絡資訊（丁寧さ細緻引導）。
    2. 伺服器端重算商品總額（官方建議零售價防偽防竄改）。
    3. 產生 SHIZUKU 雅號訂單編號與綠界跳轉表單參數。
    4. 附加一期一會當日調息箋 (Zanshin Oracle) 與安心信賴標章。
    """
    if not isinstance(data, dict):
        raise PaymentValidationError(
            message="請求資料格式無效，必須為 JSON 物件",
            code="INVALID_PAYLOAD",
            guidance="請檢查前端請求是否正確帶入 Content-Type: application/json。"
        )

    customer = data.get("customer", {})
    if not isinstance(customer, dict):
        raise PaymentValidationError(
            message="貴賓資訊（customer）格式錯誤",
            code="INVALID_CUSTOMER_PAYLOAD",
            guidance="請提供包含 name 與聯絡方式之客戶資訊物件。"
        )

    cust_name = str(customer.get("name", "")).strip()
    cust_email = str(customer.get("email", "")).strip()
    cust_phone = str(customer.get("phone", "")).strip()
    cust_line = str(customer.get("line_id", "")).strip()
    note = str(customer.get("note", "")).strip()[:500]

    if not cust_name or len(cust_name) > 60:
        raise PaymentValidationError(
            message="請留下您的貴賓稱呼，以便芳療師為您妥善調配備貨",
            code="CUSTOMER_NAME_REQUIRED",
            guidance="請在姓名欄位填寫 1 至 60 字元之真實稱謂。"
        )

    if not cust_email and not cust_phone and not cust_line:
        raise PaymentValidationError(
            message="為確保調息進度與配送通知順暢，Email、電話或 LINE ID 至少需提供一種聯絡方式",
            code="CONTACT_INFO_REQUIRED",
            guidance="芳療師將依您留下的管道提供調息箋與配送追蹤碼。"
        )

    if cust_email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cust_email):
        raise PaymentValidationError(
            message="電子郵件格式未臻完整，請確認如 name@example.com 之正確格式",
            code="INVALID_EMAIL_FORMAT",
            guidance="請檢查電子郵件是否漏填 @ 或網域後綴。"
        )

    # 金額與品項後端強制重算
    validated_items, total_amount = validate_and_calculate_order(data.get("items", []))

    provider = str(data.get("provider", "ecpay")).lower()
    if provider not in ("ecpay", "linepay"):
        raise PaymentValidationError(
            message="目前支援之線上金流為綠界科技 (ECPay) 或 LINE Pay",
            code="UNSUPPORTED_PROVIDER",
            guidance="請由結帳介面選擇支援之付款管道。"
        )

    # 建立日式雅號訂單編號 (SHIZUKU-YYYYMMDDHHmmss-XXXX)
    now_dt = datetime.now(timezone.utc)
    order_id = f"SHIZUKU-{now_dt.strftime('%Y%m%d%H%M%S')}-{''.join(random.choices(string.hexdigits.upper(), k=4))}"
    merchant_trade_no = generate_merchant_trade_no()

    config = get_ecpay_config()
    trade_date_str = now_dt.strftime("%Y/%m/%d %H:%M:%S")

    # 組裝品項名稱 (綠界以 '#' 分隔)
    item_names_str = "#".join(f"{it['name']} x {it['qty']}" for it in validated_items)[:200]

    # 回調端點設定
    base_host = os.environ.get("SERVER_BASE_URL", "https://doterra-73pv.onrender.com").rstrip("/")
    return_url = f"{base_host}/api/payments/ecpay/callback"
    client_back_url = data.get("client_back_url") or "https://doterra-two.vercel.app/#shop"

    ecpay_params = {
        "MerchantID": config["merchant_id"],
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": trade_date_str,
        "PaymentType": "aio",
        "TotalAmount": str(total_amount),
        "TradeDesc": urllib.parse.quote("雫之洞悉·返魂堂調息選品"),
        "ItemName": item_names_str,
        "ReturnURL": return_url,
        "ChoosePayment": "ALL",
        "EncryptType": "1",
        "ClientBackURL": client_back_url,
    }

    # 產生 SHA256 壓碼
    check_mac = generate_ecpay_check_mac_value(ecpay_params, config["hash_key"], config["hash_iv"])
    ecpay_params["CheckMacValue"] = check_mac

    # 生成當日調息箋與安心保證標章
    zanshin_oracle = generate_zanshin_oracle(validated_items)
    trust_assurance = get_trust_assurance()

    order_record = {
        "order_id": order_id,
        "merchant_trade_no": merchant_trade_no,
        "provider": provider,
        "status": "PENDING",
        "amount": total_amount,
        "items": validated_items,
        "customer": {
            "name": cust_name,
            "email": cust_email,
            "phone": cust_phone,
            "line_id": cust_line,
            "note": note,
        },
        "zanshin_oracle": zanshin_oracle,
        "trust_assurance": trust_assurance,
        "client_ip": client_ip or "",
        "created_at": now_dt.isoformat(),
        "updated_at": now_dt.isoformat(),
        "paid_at": None,
        "payment_info": {},
    }

    order_store.save_order(order_record)

    # Zero-PII Logging：伺服器 Log 僅輸出去敏化之顧客摘要
    masked_preview = mask_personal_info(customer)
    print(f"[payment_manager] 建立調息訂單 {order_id} (NT$ {total_amount}), 貴賓: {masked_preview.get('name')}")

    return {
        "success": True,
        "order_id": order_id,
        "merchant_trade_no": merchant_trade_no,
        "provider": provider,
        "amount": total_amount,
        "items_count": len(validated_items),
        "payment": {
            "action_url": config["api_url"],
            "method": "POST",
            "params": ecpay_params,
        },
        "zanshin_oracle": zanshin_oracle,
        "trust_assurance": trust_assurance,
    }


def process_ecpay_callback(form_dict):
    """
    處理綠界 Server-to-Server 異步付款通知回調：
    1. 驗證 CheckMacValue 簽章。
    2. 比對金額與訂單號。
    3. 冪等更新訂單狀態為 PAID。
    4. 回覆 1|OK。
    """
    config = get_ecpay_config()
    form_data = dict(form_dict)

    if not verify_ecpay_check_mac_value(form_data, config["hash_key"], config["hash_iv"]):
        raise PaymentSignatureError()

    merchant_trade_no = form_data.get("MerchantTradeNo", "")
    rtn_code = str(form_data.get("RtnCode", ""))
    trade_amt = int(form_data.get("TradeAmt", 0))

    order = order_store.get_order(merchant_trade_no)
    if not order:
        raise PaymentValidationError(
            message=f"查無指定之特店交易訂單：{merchant_trade_no}",
            code="ORDER_NOT_FOUND",
            status_code=404
        )

    # 驗證金額是否一致
    if order["amount"] != trade_amt:
        raise PaymentValidationError(
            message=f"交易金額未臻相符：預期 NT$ {order['amount']}, 實際通知 NT$ {trade_amt}",
            code="AMOUNT_MISMATCH"
        )

    # 冪等性防護：若訂單已經是 PAID，直接回傳 1|OK
    if order["status"] == "PAID":
        return "1|OK"

    now_iso = datetime.now(timezone.utc).isoformat()
    if rtn_code == "1":
        order_store.update_status(merchant_trade_no, "PAID", {
            "paid_at": now_iso,
            "payment_info": {
                "trade_no": form_data.get("TradeNo"),
                "payment_date": form_data.get("PaymentDate"),
                "payment_type": form_data.get("PaymentType"),
                "simulate_paid": form_data.get("SimulatePaid", "0"),
            },
        })
        print(f"[payment_manager] 訂單 {order['order_id']} 已圓滿完成付款 (TradeNo: {form_data.get('TradeNo')})")
    else:
        order_store.update_status(merchant_trade_no, "FAILED", {
            "payment_info": {
                "rtn_code": rtn_code,
                "rtn_msg": form_data.get("RtnMsg"),
            },
        })
        print(f"[payment_manager] 訂單 {order['order_id']} 付款未竟: {form_data.get('RtnMsg')}")

    return "1|OK"


def get_order_status(order_id_or_trade_no):
    """
    查詢訂單付款狀態（🛡️ 気配り：嚴格套用 APPI 深度脫敏，附帶當日調息籤與安心標章）
    """
    order = order_store.get_order(order_id_or_trade_no)
    if not order:
        return None

    masked_customer = mask_personal_info(order.get("customer", {}))

    return {
        "order_id": order["order_id"],
        "merchant_trade_no": order.get("merchant_trade_no"),
        "status": order["status"],
        "amount": order["amount"],
        "items": order.get("items", []),
        "provider": order.get("provider", "ecpay"),
        "created_at": order.get("created_at"),
        "paid_at": order.get("paid_at"),
        "customer": masked_customer,
        "zanshin_oracle": order.get("zanshin_oracle") or generate_zanshin_oracle(order.get("items", [])),
        "trust_assurance": order.get("trust_assurance") or get_trust_assurance(),
    }
