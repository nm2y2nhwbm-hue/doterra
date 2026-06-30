import csv
import os

def fetch_oils_data():
    csv_file = 'doterra.csv'
    
    # 嘗試幾種常見編碼
    encodings = ['utf-8-sig', 'utf-8', 'big5', 'cp950']
    
    for enc in encodings:
        try:
            with open(csv_file, mode='r', encoding=enc) as f:
                reader = csv.reader(f)
                header = next(reader) # 讀取標題
                
                oils_list = []
                for row in reader:
                    if row and row[0].strip():
                        oils_list.append({
                            "名稱": row[0].strip(),
                            "英文名稱": row[1].strip() if len(row) > 1 else "",
                            "關鍵詞": row[2].strip() if len(row) > 2 else "",
                            "心靈指引 (建議)": row[3].strip() if len(row) > 3 else "",
                            "image_url": row[4].strip() if len(row) > 4 else ""
                        })
                
                if oils_list:
                    print(f"使用編碼 {enc} 成功讀取到 {len(oils_list)} 筆資料")
                    return oils_list
        except Exception:
            continue # 如果這個編碼失敗，就試下一個

    print("錯誤：無法以任何編碼讀取 CSV")
    return []
