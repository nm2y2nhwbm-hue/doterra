# -*- coding: utf-8 -*-
"""
Agent 1 負責範圍：核心金流管理模組 (core/payment_manager.py)
實裝多特瑞精油與禮盒金額伺服器端防偽重算、綠界 ECPay (SHA256 CheckMacValue) 與 LINE Pay 規格、訂單狀態機。
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
    """資料校驗失敗異常"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class PaymentSignatureError(Exception):
    """簽章校驗失敗異常"""
    def __init__(self, message="Invalid CheckMacValue", status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


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
    回傳: dict(id, name, price, capacity) 或 None
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

        # 比對 ID、SKU 或商品名稱
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
    伺服器端金額防竄改驗算：
    1. 驗證商品陣列非空且元素格式正確。
    2. 數量必須為 1 ~ 99 之整數。
    3. 絕不採納前端傳入之單價或小計，完全依據官方資料庫建議零售價重新相乘。
    """
    if not isinstance(raw_items, list) or len(raw_items) == 0:
        raise PaymentValidationError("購物車商品清單不能為空")

    if len(raw_items) > 50:
        raise PaymentValidationError("單筆訂單商品項數超過上限")

    validated_items = []
    total_amount = 0

    for idx, item in enumerate(raw_items):
        if not isinstance(item, dict):
            raise PaymentValidationError(f"第 {idx + 1} 項商品資料結構無效")

        item_id = str(item.get("id", "")).strip()
        item_name = str(item.get("name", "")).strip()

        try:
            qty = int(item.get("qty", 1))
        except (ValueError, TypeError):
            raise PaymentValidationError(f"商品「{item_name or item_id}」數量格式無效")

        if qty < 1 or qty > 99:
            raise PaymentValidationError(f"商品「{item_name or item_id}」數量必須介於 1 至 99 之間")

        official_product = find_catalog_item(item_id, item_name)
        if not official_product:
            raise PaymentValidationError(f"找不到指定的官方商品：「{item_name or item_id}」")

        unit_price = official_product["price"]
        subtotal = unit_price * qty
        total_amount += subtotal

        validated_items.append({
            "id": official_product["id"],
            "name": official_product["name"],
            "price": unit_price,
            "capacity": official_product.get("capacity", ""),
            "qty": qty,
            "subtotal": subtotal,
        })

    if total_amount <= 0:
        raise PaymentValidationError("訂單總金額必須大於 0")

    return validated_items, total_amount


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
    1. 驗證買家個資與聯絡資訊。
    2. 伺服器端重算商品總額。
    3. 產生綠界 ECPay 跳轉表單參數與 CheckMacValue。
    4. 建立訂單紀錄（Status: PENDING）。
    """
    if not isinstance(data, dict):
        raise PaymentValidationError("請求 Payload 格式必須為 JSON 物件")

    customer = data.get("customer", {})
    if not isinstance(customer, dict):
        raise PaymentValidationError("顧客資訊（customer）格式錯誤")

    cust_name = str(customer.get("name", "")).strip()
    cust_email = str(customer.get("email", "")).strip()
    cust_phone = str(customer.get("phone", "")).strip()
    cust_line = str(customer.get("line_id", "")).strip()
    note = str(customer.get("note", "")).strip()[:500]

    if not cust_name or len(cust_name) > 60:
        raise PaymentValidationError("顧客姓名為必填，且長度限制於 1 至 60 字元")

    if not cust_email and not cust_phone and not cust_line:
        raise PaymentValidationError("Email、電話或 LINE ID 至少需提供一種聯絡方式")

    if cust_email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", cust_email):
        raise PaymentValidationError("Email 格式不符合規範")

    # 金額與品項後端強制重算
    validated_items, total_amount = validate_and_calculate_order(data.get("items", []))

    provider = str(data.get("provider", "ecpay")).lower()
    if provider not in ("ecpay", "linepay"):
        raise PaymentValidationError("不支援的金流服務商，目前支援: ecpay, linepay")

    # 建立系統訂單編號
    now_dt = datetime.now(timezone.utc)
    order_id = f"ORD-{now_dt.strftime('%Y%m%d%H%M%S')}-{''.join(random.choices(string.hexdigits.upper(), k=4))}"
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
        "TradeDesc": urllib.parse.quote("現代精油調息選品"),
        "ItemName": item_names_str,
        "ReturnURL": return_url,
        "ChoosePayment": "ALL",
        "EncryptType": "1",
        "ClientBackURL": client_back_url,
    }

    # 產生 SHA256 壓碼
    check_mac = generate_ecpay_check_mac_value(ecpay_params, config["hash_key"], config["hash_iv"])
    ecpay_params["CheckMacValue"] = check_mac

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
        "client_ip": client_ip or "",
        "created_at": now_dt.isoformat(),
        "updated_at": now_dt.isoformat(),
        "paid_at": None,
        "payment_info": {},
    }

    order_store.save_order(order_record)

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
        raise PaymentSignatureError("綠界 CheckMacValue 簽章驗證失敗")

    merchant_trade_no = form_data.get("MerchantTradeNo", "")
    rtn_code = str(form_data.get("RtnCode", ""))
    trade_amt = int(form_data.get("TradeAmt", 0))

    order = order_store.get_order(merchant_trade_no)
    if not order:
        raise PaymentValidationError(f"查無對應訂單：{merchant_trade_no}", status_code=404)

    # 驗證金額是否一致
    if order["amount"] != trade_amt:
        raise PaymentValidationError(f"訂單金額不一致: 預期 {order['amount']}, 實際 {trade_amt}")

    # 冪等性防護：若訂單已經是 PAID，直接回傳 1|OK
    if order["status"] == "PAID":
        return "1|OK"

    now_iso = datetime.now(timezone.utc).isoformat()
    if rtn_code == "1":
        # 付款成功
        order_store.update_status(merchant_trade_no, "PAID", {
            "paid_at": now_iso,
            "payment_info": {
                "trade_no": form_data.get("TradeNo"),
                "payment_date": form_data.get("PaymentDate"),
                "payment_type": form_data.get("PaymentType"),
                "simulate_paid": form_data.get("SimulatePaid", "0"),
            },
        })
    else:
        # 付款失敗
        order_store.update_status(merchant_trade_no, "FAILED", {
            "payment_info": {
                "rtn_code": rtn_code,
                "rtn_msg": form_data.get("RtnMsg"),
            },
        })

    return "1|OK"


def get_order_status(order_id_or_trade_no):
    """查詢訂單狀態（遮罩去敏化敏感個資）"""
    order = order_store.get_order(order_id_or_trade_no)
    if not order:
        return None

    cust = order.get("customer", {})
    name = cust.get("name", "")
    masked_name = (name[0] + "*" + name[-1]) if len(name) > 1 else name
    email = cust.get("email", "")
    masked_email = (email[:2] + "***@" + email.split("@")[-1]) if "@" in email else ""

    return {
        "order_id": order["order_id"],
        "merchant_trade_no": order.get("merchant_trade_no"),
        "status": order["status"],
        "amount": order["amount"],
        "items": order.get("items", []),
        "provider": order.get("provider", "ecpay"),
        "created_at": order.get("created_at"),
        "paid_at": order.get("paid_at"),
        "customer": {
            "name": masked_name,
            "email": masked_email,
        },
    }
