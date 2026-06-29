import os
import csv

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def load_essential_oils():
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return []
    
    # 讀取 CSV，確保編碼正確 (你的 CSV 為 Big5)
    with open(CSV_FILE_PATH, mode='r', encoding='Big5') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("名稱"):  # 這裡對應 CSV 的「名稱」欄位
                oils_list.append(row)
    return oils_list
