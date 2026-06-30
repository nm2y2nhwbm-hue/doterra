def fetch_oils_data():
    oils_list = []
    if not os.path.exists(CSV_FILE_PATH):
        return []
    
    try:
        # 改成 utf-8-sig，它能同時處理一般的 utf-8 以及帶有 BOM 的 utf-8
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("名稱"):
                    oils_list.append(row)
    except Exception as e:
        print(f"DEBUG: 讀取 CSV 時發生錯誤: {e}")
        return []
        
    return oils_list
