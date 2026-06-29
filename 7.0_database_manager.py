import os
import csv

# 設定檔案路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def fetch_oils_data():
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return []
    
    # 使用 Big5 編碼讀取 doterra.csv
    with open(CSV_FILE_PATH, mode='r', encoding='Big5') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 確保資料不為空
            if row.get("名稱"):
                oils_list.append(row)
    return oils_list