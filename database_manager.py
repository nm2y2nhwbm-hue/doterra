import csv

CSV_FILE_PATH = 'doterra.csv'

def fetch_oils_data():
    oils_list = []
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            # 讀取 CSV，並確保處理 Tab 分隔符或逗號
            reader = csv.DictReader(f, delimiter='\t') # 如果你的檔案是用 Tab 分隔
            # 如果讀不到資料，嘗試用逗號分隔再讀一次
            if not reader.fieldnames or "名稱" not in reader.fieldnames:
                f.seek(0)
                reader = csv.DictReader(f, delimiter=',') 
            
            for row in reader:
                # 只要名稱有資料，就加入清單
                if row.get("名稱"):
                    oils_list.append(row)
            
            print(f"成功讀取到 {len(oils_list)} 筆資料")
            return oils_list
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {e}")
        return []
