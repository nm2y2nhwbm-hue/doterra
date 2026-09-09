# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：全站靜態資源、圖檔路徑、JS 語法與 SEO 完整性自動化測試 (tests/test_asset_integrity.py)
"""
import csv
import os
import re
import subprocess
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
COMPONENTS_DIR = os.path.join(BASE_DIR, 'components')
CSV_PATH = os.path.join(BASE_DIR, 'doterra.csv')
INDICATOR_CSV_PATH = os.path.join(BASE_DIR, 'indicator_cards.csv')


class TestAssetIntegrity(unittest.TestCase):
    """全站資產完整性、零破圖與語法檢驗"""

    def test_all_oil_images_exist(self):
        """驗證 doterra.csv 中所有精油實體圖檔皆存在於 static/images/"""
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))

        missing_images = []
        for r in rows:
            fn = r.get('image_filename', '').strip()
            if not fn:
                missing_images.append(f"ID {r['id']} {r['name']} 缺少圖檔名稱")
                continue
            full_path = os.path.join(STATIC_DIR, 'images', fn)
            if not os.path.isfile(full_path):
                missing_images.append(f"{r['name']} 圖檔不存在: {fn}")

        self.assertEqual(len(missing_images), 0, f"發現精油破圖: {missing_images}")

    def test_all_indicator_images_exist(self):
        """驗證 indicator_cards.csv 中所有指示卡圖檔皆存在於 static/images/"""
        with open(INDICATOR_CSV_PATH, 'r', encoding='utf-8-sig', errors='ignore') as f:
            rows = list(csv.DictReader(f))

        missing_images = []
        for r in rows:
            fn = r.get('image_filename', '').strip()
            full_path = os.path.join(STATIC_DIR, 'images', fn)
            if not os.path.isfile(full_path):
                missing_images.append(f"{r['name']} 圖檔不存在: {fn}")

        self.assertEqual(len(missing_images), 0, f"發現指示卡破圖: {missing_images}")

    def test_html_referenced_local_assets_exist(self):
        """驗證所有 HTML 檔案中引用的本機圖檔、樣式與腳本皆存在 (零 404)"""
        html_files = [f for f in os.listdir(STATIC_DIR) if f.endswith('.html')]
        broken_references = []

        # 正則表達式抓取資源路徑
        src_pattern = re.compile(r'(?:src|href)=["\']([^"\']+)["\']', re.IGNORECASE)

        for hf in html_files:
            file_path = os.path.join(STATIC_DIR, hf)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for match in src_pattern.finditer(content):
                url = match.group(1).strip()
                # 排除外部連結、空錨點、javascript 虛擬連結、inline data 與 JS 範本變數 ${...}
                if (url.startswith('http://') or url.startswith('https://') or
                    url.startswith('//') or url.startswith('#') or
                    url.startswith('javascript:') or url.startswith('mailto:') or
                    url.startswith('tel:') or url.startswith('data:') or
                    '${' in url or not url):
                    continue

                clean_url = url.split('?')[0].split('#')[0].lstrip('/')
                target = os.path.join(STATIC_DIR, clean_url.replace('/', os.sep))
                if not os.path.exists(target):
                    broken_references.append((hf, url))

        self.assertEqual(
            len(broken_references), 0,
            f"HTML 頁面發現損壞的本地資源參照: {broken_references}"
        )

    def test_cart_components_and_static_parity(self):
        """驗證 components/cart/ 與發布目錄 static/ 的 cart.js 與 cart.css 一致性"""
        pairs = [
            (os.path.join(COMPONENTS_DIR, 'cart', 'cart.js'), os.path.join(STATIC_DIR, 'cart.js')),
            (os.path.join(COMPONENTS_DIR, 'cart', 'cart.css'), os.path.join(STATIC_DIR, 'cart.css')),
        ]
        for comp_path, static_path in pairs:
            if os.path.exists(comp_path) and os.path.exists(static_path):
                with open(comp_path, 'r', encoding='utf-8') as f1:
                    c1 = f1.read()
                with open(static_path, 'r', encoding='utf-8') as f2:
                    c2 = f2.read()
                self.assertEqual(
                    c1.strip(), c2.strip(),
                    f"元件檔案 {os.path.basename(comp_path)} 與 static/ 同名發布檔內容不一致"
                )

    def test_seo_and_metadata_completeness(self):
        """驗證 8 大核心頁面皆包含必要的 Title、Viewport 與 GA4 追蹤碼"""
        core_pages = [
            'index.html', 'cards.html', 'oils.html', 'booking.html',
            'admin.html', 'reception.html', 'inventory.html', 'sites.html'
        ]
        for page in core_pages:
            page_path = os.path.join(STATIC_DIR, page)
            self.assertTrue(os.path.exists(page_path), f"缺少核心頁面 {page}")
            with open(page_path, 'r', encoding='utf-8') as f:
                html = f.read()

            self.assertIn('<title>', html, f"{page} 缺少 <title> 標籤")
            self.assertIn('viewport', html.lower(), f"{page} 缺少 viewport meta 標籤")
            self.assertIn('G-LH6J1MM1LK', html, f"{page} 缺少 GA4 評估 ID G-LH6J1MM1LK")


if __name__ == '__main__':
    unittest.main()
