import os
import csv

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def fetch_oils_data():
    """從 CSV 檔案讀取精油資料"""
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return []
    
    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("產品名稱"): # 確保這與你的 CSV 標頭一致
                oils_list.append(row)
    return oils_list
