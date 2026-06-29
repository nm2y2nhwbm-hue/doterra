import os
import csv

# 設定檔案路徑
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def fetch_oils_data():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"錯誤：找不到檔案，檢查路徑: {CSV_FILE_PATH}")
        return []
    
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='Big5') as f:
            reader = csv.DictReader(f)
            oils_list = [row for row in reader if row.get("名稱")]
            print(f"成功讀取到 {len(oils_list)} 筆資料")
            return oils_list
    except Exception as e:
        print(f"讀取 CSV 發生錯誤: {e}")
        return []