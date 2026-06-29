import os
import csv

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def load_essential_oils():
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return []
    
    # 使用 Big5 編碼 (你的 CSV 格式)
    with open(CSV_FILE_PATH, mode='r', encoding='Big5') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 對齊 CSV 中的「名稱」欄位
            if row.get("名稱"):
                oils_list.append(row)
    return oils_list
