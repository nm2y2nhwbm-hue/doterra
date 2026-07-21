"""
獨立資料存取模組：只負責「讀 CSV → 產出乾淨的 dict 列表」。
不認識 LINE、不認識 Flex Message，只認識資料本身。
"""
import csv
import os
import urllib.parse

from core.text_utils import slugify_name_en

_THIS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(_THIS_DIR, 'doterra.csv')

# 絕對網址公式所需的環境變數，預設為 https://example.com
BASE_URL = os.environ.get('BASE_URL', 'https://example.com')

# --------------------------------------------------------------------------
# 【一鍵切換開關】
# True  = 目前尚無實體圖檔，先用 placehold.co 動態生成測試字卡，確保 Flex Message 不破圖
# False = 42 張去背實體圖已上傳到 static/images/ 之後，改為 False 切回真實圖片路徑
# --------------------------------------------------------------------------
USE_PLACEHOLDER_IMAGE = True

_CACHE = None  # 簡易記憶體快取，避免每次抽卡都重讀硬碟


def _build_placeholder_image_url(name: str, name_en: str) -> str:
    """
    動態字卡生圖公式（暫時方案，不需任何實體圖檔）：
    讀取 card['name'] 與 card['name_en']，組成 "中文名 | 英文名" 字樣，
    經 URL 編碼後帶入 placehold.co 正式生圖 API，
    確保中文、空白、"|" 等特殊字元都被正確跳脫，LINE 端 100% 能載入。

    輸出範例：
    https://placehold.co/600x400/EFE9E1/8A6D5C/png?text=%E5%A4%8F%E5%A8%81%E5%A4%B7%E6%AA%B8%E9%A6%99%E6%9C%A8%20%7C%20Sandalwood%2C%20Hawaiian
    """
    label = f"{name} | {name_en}" if name_en else name
    encoded_label = urllib.parse.quote(label)
    # 600x400 尺寸、米色底 + 咖啡色字，符合精油卡牌的溫和質感
    return f"https://placehold.co/600x400/EFE9E1/8A6D5C/png?text={encoded_label}"


def _build_real_image_url(name_en: str) -> str:
    """
    【未來正式圖檔開關】
    待 42 張去背精油圖上傳至 static/images/ 後，
    將 USE_PLACEHOLDER_IMAGE 改為 False，即會改用此函式產生的絕對路徑：

        f"{BASE_URL}/static/images/{clean_slug}.png"

    例如 name_en = "Sandalwood, Hawaiian" 會自動清洗為：
        https://your-domain.example.com/static/images/sandalwood-hawaiian.png
    """
    clean_slug = slugify_name_en(name_en)
    return f"{BASE_URL}/static/images/{clean_slug}.png"


def _build_image_url(name: str, name_en: str) -> str:
    """統一入口：依 USE_PLACEHOLDER_IMAGE 開關決定要用哪一種圖片網址。"""
    if USE_PLACEHOLDER_IMAGE:
        return _build_placeholder_image_url(name, name_en)
    return _build_real_image_url(name_en)


def fetch_oils_data(force_reload: bool = False):
    """
    讀取 doterra.csv（強制使用 utf-8-sig），
    回傳 List[dict]，每筆包含 id/name/name_en/keywords/guidance/chakra/image_url。
    """
    global _CACHE
    if _CACHE is not None and not force_reload:
        return _CACHE

    oils = []
    try:
        with open(CSV_FILE, mode='r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = (row.get('name') or '').strip()
                if not name:
                    continue
                name_en = (row.get('name_en') or '').strip()
                oils.append({
                    "id": (row.get('id') or '').strip(),
                    "name": name,
                    "name_en": name_en,
                    "keywords": (row.get('keywords') or '').strip(),
                    "guidance": (row.get('guidance') or '').strip(),
                    "chakra": (row.get('chakra') or '').strip(),
                    "image_url": _build_image_url(name, name_en),
                })
    except FileNotFoundError:
        print(f"[database_manager] 錯誤：找不到 CSV 檔案 {CSV_FILE}")
        return []
    except Exception as e:
        print(f"[database_manager] 錯誤：讀取 CSV 發生例外 -> {e}")
        return []

    _CACHE = oils
    mode_desc = "placehold.co 動態測試字卡" if USE_PLACEHOLDER_IMAGE else "static/images/ 實體圖檔"
    print(f"[database_manager] 成功讀取 {len(oils)} 筆精油資料 (utf-8-sig)，圖片來源：{mode_desc}")
    return oils


def get_oils_by_chakra(chakra: str):
    """依脈輪分類篩選卡牌，供 mode_4 使用。"""
    return [o for o in fetch_oils_data() if o.get('chakra') == chakra]


def get_all_chakras():
    """回傳目前資料庫中所有出現過的脈輪分類（去重、排序）。"""
    return sorted({o.get('chakra') for o in fetch_oils_data() if o.get('chakra')})