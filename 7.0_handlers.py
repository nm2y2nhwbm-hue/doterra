import random
from database_manager import fetch_oils_data

# 簡易記憶體，用於暫存該用戶抽到的牌
user_memory = {}

def get_drawing_response(user_id):
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中... (資料庫讀取失敗)"
    
    drawn_oil = random.choice(oils_db)
    user_memory[user_id] = drawn_oil
    
    # 返回純文字格式
    name = drawn_oil.get('產品名稱', '未知')
    keywords = drawn_oil.get('關鍵詞', '無')
    insight = drawn_oil.get('心靈指引', '無')
    
    response = f"✨ 恭喜你抽到了：{name}\n\n【關鍵詞】：{keywords}\n\n【心靈指引】：{insight}"
    return response

def get_followup_response(user_id):
    oil = user_memory.get(user_id)
    if not oil:
        return "您還沒有抽過牌喔，請輸入「抽牌」開始。"
    
    name = oil.get('產品名稱', '該精油')
    pillar = oil.get('位格歸屬', '能量位格')
    
    return f"關於「{name}」，它歸屬於「{pillar}」。在更深層的訊息中，它能協助您平衡當下的能量狀態。"
