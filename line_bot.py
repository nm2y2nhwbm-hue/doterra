import os
import sys
import csv
import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_drawing_response

# 設定環境變數
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("錯誤：請在 Render 的 Environment 中設定 CHANNEL_ACCESS_TOKEN 與 CHANNEL_SECRET")
    sys.exit(1)

app = Flask(__name__)

# 重要：這裡必須賦值給 line_bot_api
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature', '')
    try:
        handler.handle(body, signature)
    except Exception:
        traceback.print_exc()
        abort(500)
    return 'OK'

@handler.default()
def default(event):
    print(f"收到未處理事件: {event}")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(f"收到訊息: {msg}")
    
    if "抽牌" in msg:
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        if flex_json and oil_data:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
            )
        else:
            print("取得資料失敗")
    else:
        print(f"訊息不符合觸發條件: {msg}")

if __name__ == "__main__":
    app.run()
