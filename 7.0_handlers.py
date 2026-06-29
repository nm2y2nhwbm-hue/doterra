import random
import json
from database_manager import fetch_oils_data

# 簡易記憶體
user_memory = {}

def get_drawing_response(user_id):
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中... (資料庫讀取失敗)", None
    
    drawn_oil = random.choice(oils_db)
    user_memory[user_id] = drawn_oil
    
    # 建構 Flex Message 格式
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
                {"type": "text", "text": f"關鍵詞：{drawn_oil.get('關鍵詞', '無')}", "margin": "md", "weight": "regular", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": drawn_oil.get('心靈指引', '無'), "wrap": True, "margin": "md", "size": "sm"}
            ]
        }
    }
    
    # 回傳 JSON 結構，LINE SDK 接收後需以 FlexSendMessage 格式發送
    return flex_content, drawn_oil

def get_followup_response(user_id):
    oil = user_memory.get(user_id)
    if not oil:
        return "您還沒有抽過牌喔，請輸入「抽牌」開始。"
    
    name = oil.get('產品名稱', '該精油')
    pillar = oil.get('位格歸屬', '能量位格')
    
    # 這裡可以保留文字，或同樣設計一個 Flex Message
    return f"關於「{name}」，它歸屬於「{pillar}」。在更深層的訊息中，它能協助您平衡當下的能量狀態，請多加善用它的氣味來淨化思緒。"