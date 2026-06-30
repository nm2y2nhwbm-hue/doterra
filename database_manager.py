import csv

CSV_FILE_PATH = 'doterra.csv'

def fetch_oils_data():
    try:
        # 加入除錯訊息
        print(f"正在嘗試讀取: {CSV_FILE_PATH}")
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f)
            data = [row for row in reader if row.get("名稱")]
            print(f"成功讀取到 {len(data)} 筆資料")
            return data
    except FileNotFoundError:
        print(f"致命錯誤：找不到檔案 {CSV_FILE_PATH}！請確認檔案有沒有上傳到 GitHub。")
        return []
    except Exception as e:
        print(f"讀取 CSV 時發生錯誤: {e}")
        return []
