import random
from database_manager import fetch_oils_data
from linebot.models import FlexSendMessage, TextSendMessage

user_memory = {}

def get_menu_message():
    """回傳包含小語、引導、療育三個選項的選單訊息"""
    return FlexSendMessage(
        alt_text="返魂堂服務選單",
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "🌿 返魂堂精油系統", "weight": "bold", "size": "xl"},
                    {"type": "button", "action": {"type": "message", "label": "1. 療育小語 (1張)", "text": "抽牌"}},
                    {"type": "button", "action": {"type": "message", "label": "2. 心靈引導 (2張)", "text": "抽牌引導"}},
                    {"type": "button", "action": {"type": "message", "label": "3. 深度療育 (3張)", "text": "抽牌療育"}}
                ]
            }
        }
    )

def get_drawing_response(user_id, count=1):
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中...", None
    
    # 根據選單選擇的數量抽牌
    drawn_oils = random.sample(oils_db, min(count, len(oils_db)))
    user_memory[user_id] = drawn_oils
    
    reply_texts = []
    for oil in drawn_oils:
        reply_texts.append(
            f"🌿 {oil.get('產品名稱', '未知')}\n"
            f"🧘‍♂️ {oil.get('名醫建議 (專家理論基礎 + 核心效益組合)', '無建議')}"
        )
    
    return "🔮【今日指引】🔮\n\n" + "\n\n---\n\n".join(reply_texts), drawn_oils