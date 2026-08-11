"""
獨立資料存取模組：只負責「讀 CSV → 產出乾淨的 dict 列表」。
不認識 LINE、不認識 Flex Message，只認識資料本身。

本版重點：
1. 路徑解析強化，確保 Render 雲端環境下能穩定找到 doterra.csv。
2. 編碼自我修復：依序嘗試多種編碼，直到成功解析出有效資料為止。
3. 欄位完整映射：id/name/name_en/keywords/image_filename/guidance/
   chakra/description 全數讀入。
4. 圖片網址直接採用 CSV 裡的 image_filename 欄位（含副檔名，
   例如 .jpg / .png 皆可），不再由程式端自行猜測副檔名；
   只有當 CSV 該欄位為空時，才保底用 slugify_name_en() + .png
   組出檔名，避免資料缺漏時整支程式掛掉。
"""
import csv
import os
import urllib.parse
import sqlite3
import secrets
from datetime import datetime, timezone
from pathlib import Path

from core.text_utils import slugify_name_en

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent

_CANDIDATE_PATHS = [
    _PROJECT_ROOT / 'doterra.csv',
    Path.cwd() / 'doterra.csv',
]

_ENCODING_CANDIDATES = ['utf-8-sig', 'utf-8', 'big5', 'cp950', 'gb18030']

BASE_URL = os.environ.get('BASE_URL', 'https://example.com')

USE_PLACEHOLDER_IMAGE = False

_CACHE = None
_DB_PATH = Path(os.environ.get('DATABASE_PATH', str(_PROJECT_ROOT / 'doterra.sqlite3')))


def _connect():
    connection = sqlite3.connect(_DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_app_database():
    with _connect() as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS receptions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          reception_number TEXT UNIQUE NOT NULL,
          access_token TEXT UNIQUE NOT NULL,
          name TEXT NOT NULL,
          email TEXT NOT NULL,
          line_id TEXT DEFAULT '',
          preferred_date TEXT NOT NULL,
          theme TEXT NOT NULL,
          mood TEXT NOT NULL,
          question TEXT NOT NULL,
          note TEXT DEFAULT '',
          status TEXT NOT NULL DEFAULT 'waiting',
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS draws (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          access_token TEXT DEFAULT '',
          user_id TEXT DEFAULT '',
          display_name TEXT DEFAULT '',
          mode TEXT NOT NULL,
          indicator_name TEXT DEFAULT '',
          indicator_orientation TEXT DEFAULT '',
          cards TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """)


def create_reception(payload: dict):
    init_app_database()
    now = datetime.now(timezone.utc)
    reception_number = f"VIP-{now:%Y%m%d}-{secrets.token_hex(2).upper()}"
    access_token = secrets.token_urlsafe(24)
    with _connect() as connection:
        connection.execute("""
          INSERT INTO receptions
          (reception_number, access_token, name, email, line_id, preferred_date,
           theme, mood, question, note, created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (reception_number, access_token, payload['name'], payload['email'],
              payload.get('lineId', ''), payload['date'], payload['theme'],
              payload['mood'], payload['question'], payload.get('note', ''),
              now.isoformat()))
    return {'receptionNumber': reception_number, 'accessToken': access_token}


def save_draw(payload: dict):
    init_app_database()
    cards = payload.get('cards') or []
    card_text = '、'.join(c.get('name', '') if isinstance(c, dict) else str(c) for c in cards)
    with _connect() as connection:
        connection.execute("""
          INSERT INTO draws
          (access_token, user_id, display_name, mode, indicator_name,
           indicator_orientation, cards, created_at)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (payload.get('accessToken', ''), payload.get('user_id', ''),
              payload.get('display_name', ''), str(payload.get('mode', '')),
              payload.get('indicatorName', ''), payload.get('indicatorOrientation', ''),
              card_text, datetime.now(timezone.utc).isoformat()))
    return True


def admin_summary():
    init_app_database()
    with _connect() as connection:
        receptions = [dict(row) for row in connection.execute(
            "SELECT * FROM receptions ORDER BY created_at DESC LIMIT 300")]
        draws = [dict(row) for row in connection.execute(
            "SELECT * FROM draws ORDER BY created_at DESC LIMIT 300")]
    return {'receptions': receptions, 'draws': draws}


def _resolve_csv_path() -> Path:
    for path in _CANDIDATE_PATHS:
        if path.is_file():
            return path
    return _CANDIDATE_PATHS[0]


def _print_debug_directory_listing():
    print(f"[database_manager] 診斷：__file__ 實際位置 = {_THIS_FILE}")
    print(f"[database_manager] 診斷：推定專案根目錄 = {_PROJECT_ROOT}")
    print(f"[database_manager] 診斷：目前 cwd = {Path.cwd()}")
    try:
        entries = sorted(os.listdir(_PROJECT_ROOT))
        print(f"[database_manager] 診斷：{_PROJECT_ROOT} 目錄內容 = {entries}")
    except Exception as e:
        print(f"[database_manager] 診斷：無法列出 {_PROJECT_ROOT} 內容 -> {e}")


def _build_placeholder_image_url(name: str, name_en: str) -> str:
    label = f"{name} | {name_en}" if name_en else name
    encoded_label = urllib.parse.quote(label)
    return f"https://placehold.co/600x400/EFE9E1/8A6D5C/png?text={encoded_label}"


def _build_real_image_url(image_filename: str, name_en: str) -> str:
    image_filename = (image_filename or "").strip()
    if image_filename:
        return f"{BASE_URL}/static/images/{image_filename}"

    clean_slug = slugify_name_en(name_en)
    return f"{BASE_URL}/static/images/{clean_slug}.png"


def _build_image_url(name: str, name_en: str, image_filename: str = "") -> str:
    if USE_PLACEHOLDER_IMAGE:
        return _build_placeholder_image_url(name, name_en)
    return _build_real_image_url(image_filename, name_en)


def _parse_csv_with_encoding(csv_path: Path, encoding: str):
    oils = []
    with open(csv_path, mode='r', encoding=encoding, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('name') or '').strip()
            if not name:
                continue
            name_en = (row.get('name_en') or '').strip()
            image_filename = (row.get('image_filename') or '').strip()
            oils.append({
                "id": (row.get('id') or '').strip(),
                "name": name,
                "name_en": name_en,
                "keywords": (row.get('keywords') or '').strip(),
                "guidance": (row.get('guidance') or '').strip(),
                "chakra": (row.get('chakra') or '').strip(),
                "description": (row.get('description') or '').strip(),
                "image_url": _build_image_url(name, name_en, image_filename),
            })
    return oils


def fetch_oils_data(force_reload: bool = False):
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
    used_encoding = None
    errors = []

    for enc in _ENCODING_CANDIDATES:
        try:
            oils = _parse_csv_with_encoding(csv_path, enc)
            if oils:
                used_encoding = enc
                break
        except Exception as e:
            errors.append(f"{enc}: {e}")
            continue

    if not oils:
        print(f"[database_manager] 錯誤：{csv_path} 嘗試了所有編碼 {_ENCODING_CANDIDATES} 仍無法解析出有效資料")
        for err in errors:
            print(f"[database_manager] 錯誤明細 -> {err}")
        return []

    if used_encoding != 'utf-8-sig':
        print(f"[database_manager] 警告：doterra.csv 實際編碼偵測為「{used_encoding}」而非預期的 utf-8-sig。")

    _CACHE = oils
    mode_desc = "placehold.co 動態測試字卡" if USE_PLACEHOLDER_IMAGE else "static/images/ 實體圖檔"
    print(f"[database_manager] 成功讀取 {len(oils)} 筆精油資料，來源 = {csv_path}，"
          f"編碼 = {used_encoding}，圖片模式 = {mode_desc}")
    return oils


def get_oils_by_chakra(chakra: str):
    return [o for o in fetch_oils_data() if o.get('chakra') == chakra]


def get_all_chakras():
    return sorted({o.get('chakra') for o in fetch_oils_data() if o.get('chakra')})


_INDICATOR_CSV = _PROJECT_ROOT / 'indicator_cards.csv'
_INDICATOR_CACHE = None


def fetch_indicator_cards(force_reload: bool = False):
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
                    image_filename = (row.get('image_filename') or '').strip()
                    cards.append({
                        "id": (row.get('id') or '').strip(),
                        "name": name,
                        "name_en": name_en,
                        "image_url": _build_image_url(name, name_en, image_filename),
                    })
            if cards:
                break
        except Exception:
            continue

    _INDICATOR_CACHE = cards
    print(f"[database_manager] 成功讀取 {len(cards)} 張指示象徵卡")
    return cards


def get_indicator_names():
    return [c['name'] for c in fetch_indicator_cards()]
