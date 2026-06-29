import os
import csv

CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def fetch_oils_data():
    """未來如果要換成 Postgres 或 Redis，只要改這裡的程式碼即可"""
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return []
    
    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("產品名稱"):
                oils_list.append(row)
    return oils_list