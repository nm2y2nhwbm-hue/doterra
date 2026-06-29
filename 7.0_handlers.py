def get_drawing_response(user_id):
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中... (資料庫讀取失敗)", None
    
    drawn_oil = random.choice(oils_db)
    user_memory[user_id] = drawn_oil
    
    # 確保這裡的 Key 名稱與你的 CSV 標頭一致
    flex_content = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": drawn_oil.get('產品名稱', '未知'), "weight": "bold", "size": "xl", "align": "center"},
                {"type": "text", "text": drawn_oil.get('英文名稱', 'Essential Oil'), "size": "sm", "align": "center", "color": "#888888"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "image", "url": drawn_oil.get('圖片網址', 'https://via.placeholder.com/300'), "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{drawn_oil.get('關鍵詞', '無')}", "wrap": True, "margin": "md"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": drawn_oil.get('心靈指引', '無'), "wrap": True, "margin": "md", "size": "sm"}
            ]
        }
    }
    return flex_content, drawn_oil