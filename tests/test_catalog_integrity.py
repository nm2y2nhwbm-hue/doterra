# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：精油圖鑑資料庫完整性、建議零售價與法規合規測試 (tests/test_catalog_integrity.py)
"""
import csv
import json
import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'doterra.csv')
CATALOG_JSON_PATH = os.path.join(BASE_DIR, 'static', 'oils-catalog.json')
INDEX_HTML_PATH = os.path.join(BASE_DIR, 'static', 'index.html')


class TestCatalogIntegrity(unittest.TestCase):
    """檢驗圖鑑母體、建議零售價、官方容量與法規用詞合規"""

    def setUp(self):
        self.assertTrue(os.path.exists(CSV_PATH), f"找不到資料庫檔案: {CSV_PATH}")
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.rows = list(reader)

    def test_csv_row_count(self):
        """驗證精油資料列數不為空"""
        self.assertGreaterEqual(len(self.rows), 60, "精油資料筆數過少，可能有資料遺失")

    def test_csv_required_fields(self):
        """驗證每筆精油皆包含必要欄位且不為空"""
        required_fields = ['id', 'name', 'name_en', 'sku', 'capacity', 'pillar', 'price_retail']
        for row in self.rows:
            for field in required_fields:
                self.assertIn(field, row, f"缺少欄位 {field}")
                self.assertTrue(str(row[field]).strip(), f"ID {row.get('id')} 缺少 {field} 數值")

    def test_retail_prices_positive_integers(self):
        """驗證建議零售價必須大於 0 且為正整數"""
        for row in self.rows:
            raw_price = row.get('price_retail') or row.get('price')
            self.assertIsNotNone(raw_price, f"{row['name']} 缺少零售價格")
            price = int(raw_price)
            self.assertGreater(price, 0, f"{row['name']} 價格必須大於 0，當前為 {price}")

    def test_capacity_specifications(self):
        """驗證容量標記必須符合多特瑞官方標準 (15ml / 5ml / 10ml 滾珠 / 115ml)"""
        valid_volumes = ['15ml', '5ml', '10ml', '115ml']
        for row in self.rows:
            cap = row.get('capacity', '')
            matched = any(v in cap for v in valid_volumes)
            self.assertTrue(matched, f"{row['name']} 容量標記異常: '{cap}'，應符合 15ml / 5ml / 10ml / 115ml")

    def test_skus_format_and_status(self):
        """驗證商品 SKU 編號欄位格式與待補清單追蹤"""
        pending_skus = []
        assigned_skus = []
        for r in self.rows:
            sku = r.get('sku', '').strip()
            self.assertTrue(sku, f"{r['name']} 缺少 SKU 欄位")
            if '(待補)' in sku or '待補' in sku:
                pending_skus.append((r['id'], r['name']))
            else:
                assigned_skus.append(sku)

        # 確保已編號之 SKU 格式符合 8 位數字標準
        for sku in assigned_skus:
            self.assertTrue(re.match(r'^\d{8}$', sku), f"SKU 編號格式非 8 位數字: {sku}")

    def test_compliance_natural_medicine_wording(self):
        """法規遵循性稽核：確保排除高風險醫療詞彙（如古法中醫、名醫、治癒、療效），全數採用自然醫學"""
        forbidden_keywords = ['古法中醫', '名醫', '治癒', '處方治療']
        for row in self.rows:
            advice = row.get('doctor_advice', '')
            desc = row.get('description', '')
            combined = advice + " " + desc
            for kw in forbidden_keywords:
                self.assertNotIn(kw, combined, f"{row['name']} 出現法規風險關鍵字 '{kw}'，應替換為自然醫學用語")

    def test_json_catalog_synchronization(self):
        """驗證 static/oils-catalog.json 與 CSV 母體資料筆數與定價同步"""
        self.assertTrue(os.path.exists(CATALOG_JSON_PATH), "缺少 static/oils-catalog.json")
        with open(CATALOG_JSON_PATH, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        self.assertEqual(len(catalog), len(self.rows), "oils-catalog.json 筆數與 doterra.csv 不一致")
        for item in catalog:
            self.assertIn('price_retail', item)
            self.assertGreater(int(item['price_retail']), 0)

    def test_shop_gift_sets_pricing(self):
        """驗證首頁 4 大調息禮盒建議零售價格設定"""
        expected_gifts = {
            '【鏡子】當下覺察調息禮盒': 1845,
            '【河流】時間軌跡梳理禮盒': 1965,
            '【岔路】重大抉擇守護禮盒': 4895,
            '【客製】專屬位格滾珠精油': 1040,
        }
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as f:
            html = f.read()

        for name, price in expected_gifts.items():
            self.assertIn(name, html, f"首頁缺少禮盒: {name}")
            price_str = f"{price:,}"
            self.assertTrue(
                str(price) in html or price_str in html,
                f"首頁禮盒 {name} 未標註正確建議零售價 NT$ {price}"
            )


if __name__ == '__main__':
    unittest.main()
