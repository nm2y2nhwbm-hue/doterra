import random
from database_manager import fetch_oils_data

# 簡易記憶體：紀錄每個用戶最近一次抽到的牌
user_memory = {}

def get_drawing_response(user_id):
    try:
        oils_db = fetch_oils_data()
        if not oils_db:
            return "❌ 資料庫回傳為空，請檢查資料夾路徑與 CSV 格式。", None
        
        drawn_oil = random.choice(oils_db)
        # ... 後續程式碼 ...
        
    except Exception as e:
        return f"🚨 系統發生錯誤：{str(e)}", None
        f"🔮【返魂堂·精油洞悉卡今日指引】🔮\n\n"
        f"🌿 今日有緣精油：{drawn_oil.get('產品名稱', '未知')}\n"
        f"📐 能量位格歸屬：{drawn_oil.get('位格歸屬', '未知')}\n\n"
        f"🧘‍♂️ 心靈指引：\n{drawn_oil.get('名醫建議 (專家理論基礎 + 核心效益組合)', '無建議')}\n\n"
        f"====================\n"
        f"🛠️【日常使用與防護指南】\n"
        f"• 使用方式：{drawn_oil.get('用法標籤', '無')}\n"
        f"• 塗抹建議：{drawn_oil.get('塗抹建議', '無')}"
    )
    return reply, drawn_oil

def get_followup_response(user_id):
    """處理用戶的追問"""
    oil = user_memory.get(user_id)
    if not oil:
        return "您還沒有抽過牌喔，請輸入「抽牌」開始。"
    
    # 擴充：利用 get() 方法確保即使欄位為空也不會崩潰
    name = oil.get('產品名稱', '該精油')
    pillar = oil.get('位格歸屬', '能量位格')
    
    return f"關於「{name}」，它歸屬於「{pillar}」。在更深層的訊息中，它能協助您平衡當下的能量狀態，請多加善用它的氣味來淨化思緒。"