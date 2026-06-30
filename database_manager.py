import csv

CSV_FILE_PATH = 'doterra.csv'

def fetch_oils_data():
    oils_list = []
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            lines = f.readlines()
            print(f"總共讀取到 {len(lines)} 行原始資料")
            
            # 從第二行開始讀取 (跳過標題)
            for i, line in enumerate(lines[1:]):
                # 用 Tab 或 逗號來拆解
                row = line.strip().replace('\t', ',').split(',')
                # 如果這行有資料，就加入
                if len(row) >= 1 and row[0].strip():
                    oils_list.append({
                        "名稱": row[0].strip(),
                        "英文名稱": row[1].strip() if len(row) > 1 else "",
                        "關鍵詞": row[2].strip() if len(row) > 2 else "",
                        "心靈指引 (建議)": row[3].strip() if len(row) > 3 else "",
                        "image_url": row[4].strip() if len(row) > 4 else ""
                    })
            
            print(f"成功處理後得到 {len(oils_list)} 筆資料")
            return oils_list
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {e}")
        return []
