import csv

# 直接寫死檔案名稱，不使用 os 模組，這樣就不會再有 NameError
CSV_FILE_PATH = 'doterra.csv'

def fetch_oils_data():
    try:
        # 假設 csv 檔案跟程式碼在同一個目錄
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f)
            # 過濾掉沒有名稱的空列
            return [row for row in reader if row.get("名稱")]
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {CSV_FILE_PATH}")
        return []
    except Exception as e:
        print(f"讀取 CSV 時發生其他錯誤: {e}")
        return []
