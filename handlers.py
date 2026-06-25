import random
from database_manager import fetch_oils_data

# 簡易記憶體：紀錄每個用戶最近一次抽到的牌
# 格式: {user_id: oil_data}
user_memory = {}

def get_drawing_response(user_id):
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中...", None
    
    drawn_oil = random.choice(oils_db)
    
    # 將結果存入記憶體
    user_memory[user_id] = drawn_oil
    
    reply = (
        f"🔮【返魂堂·精油洞悉卡今日指引】🔮\n\n"
        f"🌿 今日有緣精油：{drawn_oil.get('產品名稱')}\n"
        f"📐 能量位格歸屬：{drawn_oil.get('位格歸屬')}\n\n"
        f"🧘‍♂️ 心靈指引：\n{drawn_oil.get('名醫建議 (專家理論基礎 + 核心效益組合)')}\n\n"
        f"====================\n"
        f"🛠️【日常使用與防護指南】\n"
        f"• 使用方式：{drawn_oil.get('用法標籤')}\n"
        f"• 塗抹建議：{drawn_oil.get('塗抹建議')}"
    )
    return reply, drawn_oil

def get_followup_response(user_id):
    """處理用戶的追問，例如 '再多解釋一點'"""
    oil = user_memory.get(user_id)
    if not oil:
        return "您還沒有抽過牌喔，請輸入「抽牌」開始。"
    
    # 這裡可以擴充你針對該精油的「進階解說」內容
    return f"關於「{oil.get('產品名稱')}」，其實它在能量位格中還有更深層的訊息..."