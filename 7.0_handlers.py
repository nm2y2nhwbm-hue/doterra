import random
from database_manager import fetch_oils_data

# 簡易記憶體
user_memory = {}

def get_drawing_response(user_id):
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中... (資料庫讀取失敗)", None
    
    drawn_oil = random.choice(oils_db)
    user_memory[user_id] = drawn_oil
    
    # 對應 CSV 欄位名稱
    flex_content = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": drawn_oil.get('名稱', '未知'), "weight": "bold", "size": "xl", "align": "center"},
                {"type": "text", "text": drawn_oil.get('英文名稱', 'Essential Oil'), "size": "sm", "align": "center", "color": "#888888"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "image", "url": drawn_oil.get('image_url') or 'https://via.placeholder.com/300', "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{drawn_oil.get('關鍵詞', '無')}", "margin": "md", "weight": "regular", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": drawn_oil.get('心靈指引 (建議)', '無'), "wrap": True, "margin": "md", "size": "sm"}
            ]
        }
    }
    return flex_content, drawn_oil