import os
import csv

# 設定檔案路徑：確保在任何環境下都能正確讀取
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.join(BASE_DIR, 'doterra.csv')

def fetch_oils_data():
    """
    從 doterra.csv 讀取精油資料，回傳字典列表
    """
    oils_list = []
    
    # 檢查檔案是否存在
    if not os.path.exists(CSV_FILE_PATH):
        print(f"DEBUG: 找不到檔案 {CSV_FILE_PATH}")
        return []
    
    try:
        # 使用 Big5 編碼讀取 (你的 CSV 目前是這個編碼)
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 確保名稱欄位有資料才加入
                if row.get("名稱"):
                    oils_list.append(row)
    except Exception as e:
        print(f"DEBUG: 讀取 CSV 時發生錯誤: {e}")
        return []
        
    return oils_list
