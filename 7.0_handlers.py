import random
from database_manager import fetch_oils_data

# 用戶記憶暫存
user_memory = {}

def get_drawing_response(user_id):
    oils_db = fetch_oils_data()
    if not oils_db:
        return None, "🔮 系統維護中... (資料庫讀取失敗)"
    
    drawn_oil = random.choice(oils_db)
    user_memory[user_id] = drawn_oil
    
    # Flex Message 結構定義
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

def get_followup_response(user_id):
    oil = user_memory.get(user_id)
    if not oil:
        return "您還沒有抽過牌喔，請輸入「抽牌」開始。"
    return f"關於「{oil.get('產品名稱')}」，建議您在日常中使用它來協助平衡當下的能量狀態。"