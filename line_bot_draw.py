import os
import csv
import random
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ======================================================
# 🔑 LINE 官方帳號金鑰設定 (已自動保留你原本的正確金鑰)
# ======================================================
CHANNEL_SECRET = 'eea492cdcc8c24ddc585e72367ec86fd'
CHANNEL_ACCESS_TOKEN = '4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ======================================================
# 📊 CSV 資料庫全自動讀取核心 (已精準對齊 doterra.csv)
# ======================================================
CSV_FILE_PATH = os.path.join(os.path.dirname(__file__), 'doterra.csv')

def load_essential_oils():
    """自動從 doterra.csv 讀取多特瑞精油資料"""
    oils_list = []
    
    if not os.path.exists(CSV_FILE_PATH):
        print(f"⚠️ 警告：找不到 {CSV_FILE_PATH}，啟用臨時測試模式！")
        return [{
            "產品名稱": "精油資料庫對接中", 
            "用法標籤": "薰香", 
            "塗抹建議": "直塗", 
            "位格歸屬": "中柱", 
            "名醫建議 (專家理論基礎 + 核心效益組合)": "請確認 doterra.csv 是否已正確放置於 office 資料夾中。"
        }]
        
    try:
        with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 確保只抓取有產品名稱的有效行，並過濾掉「待補」或空白欄位
                if row.get("產品名稱") and "編號" not in row.get("產品名稱"):
                    oils_list.append(row)
    except Exception as e:
        print(f"❌ 讀取 CSV 發生錯誤: {e}")
        
    return oils_list

# ======================================================
# 📡 LINE Webhook 接收端點
# ======================================================
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("⚠️ 簽章驗證失敗，可能是 Verify 按鈕觸發")
        abort(400)
    except Exception as e:
        print(f"❌ 處理訊息時發生未預期錯誤: {e}")
        abort(500)
        
    return 'OK'

# ======================================================
# 🔮 抽牌核心邏輯與訊息回傳
# ======================================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    
    # 只要客人的關鍵字包含「抽牌」、「抽卡」或「今日」
    if "抽牌" in user_msg or "抽卡" in user_msg or "今日" in user_msg or user_msg.lower() == "draw":
        oils_db = load_essential_oils()
        
        if not oils_db:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔮 系統架設中，請稍後再試！"))
            return
            
        # 隨機抽取一支精油
        drawn_oil = random.choice(oils_db)
        
        # 從 CSV 欄位中精準撈取對應資料
        oil_name = drawn_oil.get("產品名稱", "未知精油")
        usage = drawn_oil.get("用法標籤", "薰香、塗抹")
        apply_suggest = drawn_oil.get("塗抹建議", "直塗")
        pillar = drawn_oil.get("位格歸屬", "未知位格")
        expert_advice = drawn_oil.get("名醫建議 (專家理論基礎 + 核心效益組合)", "暫無心靈指引")
        
        # 組合出充滿儀式感的返魂堂回覆文字
        reply_msg = (
            f"🔮【返魂堂·精油洞悉卡今日指引】🔮\n\n"
            f"🌿 今日有緣精油：{oil_name}\n"
            f"📐 能量位格歸屬：{pillar}\n\n"
            f"🧘‍♂️ 芳療心靈盲點與建議：\n"
            f"{expert_advice}\n\n"
            f"====================\n"
            f"🛠️【日常使用與防護指南】\n"
            f"• 使用方式：{usage}\n"
            f"• 塗抹建議：{apply_suggest}\n\n"
            f"✨ 讓大自然的植物頻率，校正你今日的身心和諧。 🙏"
        )
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))
    else:
        # 如果客人輸入其他日常對話，給予溫暖的自動引導回應
        welcome_msg = (
            f"🙏 歡迎光臨返魂堂！\n\n"
            f"請輸入「精油洞悉卡抽牌」，或者點擊下方的選單，即可為您抽取今日的身心精油指引與多特瑞使用建議唷！"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_msg))

if __name__ == "__main__":
    app.run(port=5000, debug=False)