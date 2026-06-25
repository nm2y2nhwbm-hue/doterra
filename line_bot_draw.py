from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# 匯入我們定義好的 handler 函數
from handlers import get_drawing_response, get_followup_response
import os

app = Flask(__name__)

# 從環境變數讀取金鑰，確保部署安全
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

@app.route("/", methods=['GET'])
def index():
    return "返魂堂機器人運作中 (Webhook 連接正常)"

@app.route("/callback", methods=['POST'])
def callback():
    # 獲取簽章與內容
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    
    # 處理 Webhook 請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("簽章驗證失敗，請檢查 CHANNEL_SECRET 設定")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id 
    user_text = event.message.text
    
    try:
        # 邏輯分流：抽牌 vs. 追問解釋
        if any(k in user_text for k in ["抽牌", "抽卡", "draw"]):
            reply, _ = get_drawing_response(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            
        elif any(k in user_text for k in ["解釋", "更多", "說明"]):
            reply = get_followup_response(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            
    except Exception as e:
        # 當伺服器發生意外錯誤時，記錄 Log 並回饋用戶
        print(f"Error: {e}") 
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="🔮 系統暫時迷路了，請再試一次或輸入「抽牌」重新開始。")
        )

if __name__ == "__main__":
    # 使用 Render 提供的 PORT，預設為 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)