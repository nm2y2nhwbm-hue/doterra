# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：商品目錄同步腳本與資料庫對齊深度測試 (tests/test_catalog_sync.py)
檢驗 Agent 4 之 catalog/sync_catalog.py 執行邏輯、冪等性，以及 doterra.csv 與 oils-catalog.json 1:1 精準映射。
"""
import csv
import json
import os
import sys
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'doterra.csv')
CATALOG_JSON_PATH = os.path.join(BASE_DIR, 'static', 'oils-catalog.json')
SYNC_SCRIPT_PATH = os.path.join(BASE_DIR, 'catalog', 'sync_catalog.py')


class TestCatalogSync(unittest.TestCase):
    """深度測試商品目錄同步腳本與資料完整性"""

    def setUp(self):
        self.assertTrue(os.path.exists(CSV_PATH), f"找不到商品母體: {CSV_PATH}")
        self.assertTrue(os.path.exists(SYNC_SCRIPT_PATH), f"找不到同步腳本: {SYNC_SCRIPT_PATH}")

    def test_sync_script_execution_and_idempotency(self):
        """驗證 catalog/sync_catalog.py 可重複執行且具備冪等性"""
        # 動態匯入 catalog/sync_catalog.py 的 sync_catalog 函式
        sys.path.insert(0, os.path.join(BASE_DIR, 'catalog'))
        try:
            import sync_catalog
            count1 = sync_catalog.sync_catalog()
            self.assertGreaterEqual(count1, 60, "同步商品筆數過少")

            # 第二次執行確認冪等性
            count2 = sync_catalog.sync_catalog()
            self.assertEqual(count1, count2, "多次執行同步腳本商品筆數不一致")
        finally:
            if os.path.join(BASE_DIR, 'catalog') in sys.path:
                sys.path.remove(os.path.join(BASE_DIR, 'catalog'))

    def test_csv_and_json_exact_matching(self):
        """驗證 doterra.csv 與 static/oils-catalog.json 每一筆資料之關鍵欄位 1:1 精確一致"""
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            csv_rows = [r for r in csv.DictReader(f) if (r.get('name') or '').strip()]

        with open(CATALOG_JSON_PATH, 'r', encoding='utf-8') as f:
            json_rows = json.load(f)

        self.assertEqual(len(csv_rows), len(json_rows), "CSV 與 JSON 總筆數不一致")

        # 建立 ID 索引對照
        json_map = {item['id']: item for item in json_rows}

        for csv_item in csv_rows:
            item_id = csv_item['id'].strip()
            self.assertIn(item_id, json_map, f"JSON 中缺少 CSV 商品 ID: {item_id}")
            json_item = json_map[item_id]

            # 驗證名稱對齊
            self.assertEqual(csv_item['name'].strip(), json_item['name'])
            self.assertEqual(csv_item['name_en'].strip(), json_item['name_en'])

            # 驗證建議零售價
            csv_price_raw = csv_item.get('price_retail') or csv_item.get('price') or '0'
            expected_price = int(csv_price_raw.strip()) if csv_price_raw.strip().isdigit() else 0
            self.assertEqual(json_item['price_retail'], expected_price, f"{json_item['name']} 建議零售價不符")
            self.assertEqual(json_item['price'], expected_price, f"{json_item['name']} 價格欄位未同步")

            # 驗證官方標準容量
            self.assertEqual(csv_item['capacity'].strip(), json_item['capacity'])
            self.assertTrue(
                any(v in json_item['capacity'] for v in ['15ml', '5ml', '10ml', '115ml']),
                f"{json_item['name']} 容量規格非官方標準: {json_item['capacity']}"
            )

            # 驗證圖檔名稱不為空
            self.assertTrue(json_item['image_filename'], f"{json_item['name']} 缺少圖檔名稱")

    def test_all_catalog_items_have_valid_pillars(self):
        """驗證所有商品皆正確歸屬於「中柱 (Balance)、左柱 (Severity / 陰)、右柱 (Mercy / 陽)」三大位格之一"""
        valid_pillars = {'中柱 (Balance)', '左柱 (Severity / 陰)', '右柱 (Mercy / 陽)'}
        with open(CATALOG_JSON_PATH, 'r', encoding='utf-8') as f:
            items = json.load(f)

        for item in items:
            pillar = item.get('pillar', '').strip()
            self.assertIn(
                pillar, valid_pillars,
                f"商品 {item['name']} 位格異常: '{pillar}'，應為 中柱/左柱/右柱"
            )


if __name__ == '__main__':
    unittest.main()
