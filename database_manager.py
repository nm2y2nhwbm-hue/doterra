import csv
import os

def fetch_oils_data():
    # 偵測當前目錄下的檔案
    files = os.listdir('.')
    print(f"目前目錄下的檔案清單: {files}")
    
    csv_file = 'doterra.csv'
    if csv_file not in files:
        print(f"致命錯誤：找不到 {csv_file}！它不在程式目錄下。")
        return []

    try:
        with open(csv_file, mode='r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if not content:
                print("檔案是空的！")
                return []
            
            lines = content.splitlines()
            print(f"檔案內容長度: {len(content)} 字元，共 {len(lines)} 行")
            return [] # 這裡先回傳空，讓我們看 Log 的輸出
    except Exception as e:
        print(f"讀取時發生錯誤: {e}")
        return []
