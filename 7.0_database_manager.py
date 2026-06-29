# database_manager.py 修改範例
def load_essential_oils():
    # ... (前面的讀取程式)
    for row in reader:
        # 使用現有檔案的「名稱」欄位作為產品名稱
        # 若需要其他欄位，請對應到正確的 CSV 標頭
        if row.get("名稱"): 
            oils_list.append({
                "產品名稱": row.get("名稱"),
                "心靈指引": row.get("心靈指引 (建議)"),
                "圖片網址": row.get("image_url"),
                # 其他欄位如果沒有，可以先給預設值
                "位格歸屬": "未定義",
                "塗抹建議": "請參考說明書"
            })
    return oils_list
