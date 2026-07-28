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


def fetch_oils_data(force_reload:
