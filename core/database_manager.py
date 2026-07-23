"""
獨立資料存取模組：只負責「讀 CSV → 產出乾淨的 dict 列表」。
不認識 LINE、不認識 Flex Message，只認識資料本身。

本版重點：針對 Render 雲端部署環境強化路徑解析與錯誤診斷，
確保 doterra.csv 不管在 Render 或本機都能被穩定找到；
若真的找不到，會印出詳細 log 協助排查，而不是默默回傳空列表。
"""
import csv
import os
import urllib.parse
from pathlib import Path

from core.text_utils import slugify_name_en

# --------------------------------------------------------------------------
# 路徑解析：以「這支檔案自己的實際位置」為基準往上找專案根目錄，
# 完全不依賴「執行時的 Working Directory」（cwd 在 gunicorn / Render 下
# 有時會跟你以為的不一樣，但 __file__ 的絕對路徑永遠可靠）。
#
#   core/database_manager.py
#   └── .parent        -> core/
#       └── .parent    -> 專案根目錄（doterra.csv 應該在這裡）
# --------------------------------------------------------------------------
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent

# 候選路徑清單（依優先順序嘗試）：
#   1. 專案根目錄下的 doterra.csv（標準預期位置）
#   2. 執行時的 cwd 下的 doterra.csv（保底，因應極少數部署平台改變 entrypoint 位置）
_CANDIDATE_PATHS = [
    _PROJECT_ROOT / 'doterra.csv',
    Path.cwd() / 'doterra.csv',
]

# 絕對網址公式所需的環境變數，預設為 https://example.com
BASE_URL = os.environ.get('BASE_URL', 'https://example.com')

# --------------------------------------------------------------------------
# 【一鍵切換開關】
# True  = 目前尚無實體圖檔，先用 placehold.co 動態生成測試字卡，確保 Flex Message 不破圖
# False = 42 張去背實體圖已上傳到 static/images/ 之後，改為 False 切回真實圖片路徑
# --------------------------------------------------------------------------
USE_PLACEHOLDER_IMAGE = True

_CACHE = None  # 簡易記憶體快取，避免每次抽卡都重讀硬碟


def _resolve_csv_path() -> Path:
    """
    依序嘗試候選路徑，回傳第一個實際存在的檔案路徑。
    若全部都找不到，回傳第一個候選路徑（讓後續的 open() 拋出明確錯誤，並印出診斷資訊）。
    """
    for path in _CANDIDATE_PATHS:
        if path.is_file():
            return path
    return _CANDIDATE_PATHS[0]


def _print_debug_directory_listing():
    """
    找不到 CSV 時的診斷輔助：把專案根目錄實際內容印出來，
    方便直接對照 Render Logs，確認到底是路徑錯、檔名錯，還是根本沒被 commit 上去。
    """
    print(f"[database_manager] 診斷：__file__ 實際位置 = {_THIS_FILE}")
    print(f"[database_manager] 診斷：推定專案根目錄 = {_PROJECT_ROOT}")
    print(f"[database_manager] 診斷：目前 cwd = {Path.cwd()}")
    try:
        entries = sorted(os.listdir(_PROJECT_ROOT))
        print(f"[database_manager] 診斷：{_PROJECT_ROOT} 目錄內容 = {entries}")
    except Exception as e:
        print(f"[database_manager] 診斷：無法列出 {_PROJECT_ROOT} 內容 -> {e}")


def _build_placeholder_image_url(name: str, name_en: str) -> str:
    """
    動態字卡生圖公式（暫時方案，不需任何實體圖檔）：
    讀取 card['name'] 與 card['name_en']，組成 "中文名 | 英文名" 字樣，
    經 URL 編碼後帶入 placehold.co 正式生圖 API，
    確保中文、空白、"|" 等特殊字元都被正確跳脫，LINE 端 100% 能載入。
    """
    label = f"{name} | {name_en}" if name_en else name
    encoded_label = urllib.parse.quote(label)
    return f"https://placehold.co/600x400/EFE9E1/8A6D5C/png?text={encoded_label}"


def _build_real_image_url(name_en: str) -> str:
    """
    【未來正式圖檔開關】
    待 42 張去背精油圖上傳至 static/images/ 後，
    將 USE_PLACEHOLDER_IMAGE 改為 False，即會改用此函式產生的絕對路徑：

        f"{BASE_URL}/static/images/{clean_slug}.png"
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

    csv_path = _resolve_csv_path()

    if not csv_path.is_file():
        print(f"[database_manager] 錯誤：在所有候選路徑都找不到 doterra.csv")
        print(f"[database_manager] 錯誤：已嘗試路徑 = {[str(p) for p in _CANDIDATE_PATHS]}")
        _print_debug_directory_listing()
        return []

    oils = []
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig', newline='') as f:
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
    except Exception as e:
        print(f"[database_manager] 錯誤：讀取 {csv_path} 發生例外 -> {e}")
        return []

    if not oils:
        print(f"[database_manager] 警告：{csv_path} 已成功開啟，但解析出 0 筆有效資料（請檢查標題列與欄名是否為 id,name,name_en,keywords,guidance,chakra）")

    _CACHE = oils
    mode_desc = "placehold.co 動態測試字卡" if USE_PLACEHOLDER_IMAGE else "static/images/ 實體圖檔"
    print(f"[database_manager] 成功讀取 {len(oils)} 筆精油資料，來源 = {csv_path}，圖片模式 = {mode_desc}")
    return oils


def get_oils_by_chakra(chakra: str):
    """依脈輪分類篩選卡牌，供 mode_4 使用。"""
    return [o for o in fetch_oils_data() if o.get('chakra') == chakra]


def get_all_chakras():
    """回傳目前資料庫中所有出現過的脈輪分類（去重、排序）。"""
    return sorted({o.get('chakra') for o in fetch_oils_data() if o.get('chakra')})
_INDICATOR_CSV = _PROJECT_ROOT / 'indicator_cards.csv'
_INDICATOR_CACHE = None


def fetch_indicator_cards(force_reload: bool = False):
    """
    讀取 indicator_cards.csv（雷諾曼指示象徵卡，12 張，獨立於精油卡資料庫）。
    回傳 List[dict]，每筆包含 id/name/name_en/image_url。
    """
    global _INDICATOR_CACHE
    if _INDICATOR_CACHE is not None and not force_reload:
        return _INDICATOR_CACHE

    if not _INDICATOR_CSV.is_file():
        print(f"[database_manager] 錯誤：找不到指示卡 CSV {_INDICATOR_CSV}")
        return []

    cards = []
    for enc in _ENCODING_CANDIDATES:
        try:
            cards = []
            with open(_INDICATOR_CSV, mode='r', encoding=enc, newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = (row.get('name') or '').strip()
                    if not name:
                        continue
                    name_en = (row.get('name_en') or '').strip()
                    cards.append({
                        "id": (row.get('id') or '').strip(),
                        "name": name,
                        "name_en": name_en,
                        "image_url": _build_image_url(name, name_en),
                    })
            if cards:
                break
        except Exception:
            continue

    _INDICATOR_CACHE = cards
    print(f"[database_manager] 成功讀取 {len(cards)} 張指示象徵卡")
    return cards


def get_indicator_names():
    """回傳所有指示卡的中文名稱清單，供 router.py 比對觸發字使用。"""
    return [c['name'] for c in fetch_indicator_cards()]
