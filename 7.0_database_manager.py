import os
import csv

# 設定 CSV 路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def fetch_oils_data():
    """讀取 CSV 資料並轉換為字典列表"""
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        print(f"找不到檔案: {CSV_FILE_PATH}")
        return []
    
    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 確保有產品名稱才加入列表
            if row.get("產品名稱"):
                oils_list.append(row)
    return oils_list