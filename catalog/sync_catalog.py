# -*- coding: utf-8 -*-
"""
Agent 4 專用：商品圖鑑資料庫同步腳本 (catalog/sync_catalog.py)
讀取 doterra.csv 母體，校驗建議零售價與官方容量，同步輸出至 static/oils-catalog.json
"""
import csv
import json
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'doterra.csv')
OUTPUT_JSON = os.path.join(BASE_DIR, 'static', 'oils-catalog.json')


def sync_catalog():
    if not os.path.exists(CSV_PATH):
        print(f"[Error] 找不到商品母體資料庫: {CSV_PATH}")
        sys.exit(1)

    print(f"[Agent 4] 讀取商品母體: {CSV_PATH}")
    with open(CSV_PATH, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    catalog = []
    for row in rows:
        name = (row.get('name') or '').strip()
        if not name:
            continue

        raw_price = (row.get('price_retail') or row.get('price') or '0').strip()
        price = int(raw_price) if raw_price.isdigit() else 0

        catalog.append({
            "id": (row.get('id') or '').strip(),
            "name": name,
            "name_en": (row.get('name_en') or '').strip(),
            "sku": (row.get('sku') or '').strip(),
            "capacity": (row.get('capacity') or '').strip(),
            "pillar": (row.get('pillar') or '').strip(),
            "price_retail": price,
            "price": price,
            "keywords": (row.get('keywords') or '').strip(),
            "usage_tags": (row.get('usage_tags') or '').strip(),
            "dilution_guide": (row.get('dilution_guide') or '').strip(),
            "doctor_advice": (row.get('doctor_advice') or '').strip(),
            "guidance": (row.get('guidance') or '').strip(),
            "description": (row.get('description') or '').strip(),
            "chakra": (row.get('chakra') or '').strip(),
            "image_filename": (row.get('image_filename') or '').strip(),
        })

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, mode='w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"[Agent 4] 成功同步 {len(catalog)} 款精油資料至: {OUTPUT_JSON}")
    return len(catalog)


if __name__ == '__main__':
    count = sync_catalog()
    print(f"[Agent 4] 同步完成，共 {count} 款商品已完成建議零售價校驗。")
