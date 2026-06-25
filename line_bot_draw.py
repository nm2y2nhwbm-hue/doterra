from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
# 匯入我們定義好的 handler 函數
from handlers import get_drawing_response, get_followup_response
import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    handler.handle(request.get_data(as_text=True), request.headers.get('X-Line-Signature'))
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 1. 取得用戶的唯一 ID
    user_id = event.source.user_id 
    user_text = event.message.text
    
    # 2. 判斷邏輯
    if any(k in user_text for k in ["抽牌", "抽卡", "draw"]):
        # 傳遞 user_id 給 handler
        reply, _ = get_drawing_response(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        
    elif any(k in user_text for k in ["解釋", "更多", "說明"]):
        # 傳遞 user_id 進行追問邏輯
        reply = get_followup_response(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 5000)))