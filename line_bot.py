import os
import sys
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_drawing_response

# 1. 檢查環境變數是否設定
# 這些變數請去 Render Dashboard 的 Environment 設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("錯誤：請在 Render 的 Environment 中設定 CHANNEL_ACCESS_TOKEN 與 CHANNEL_SECRET")
    sys.exit(1) # 強制停止，這樣你能在 Logs 看到這行錯誤

app = Flask(__name__)

LineBotApi('4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('eea492cdcc8c24ddc585e72367ec86fd')


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "抽牌":
        # 取得 flex_json 與資料
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        
        # 增加防呆：確保有資料才發送
        if flex_json and oil_data:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
            )

if __name__ == "__main__":
    app.run()
# trigger deployment
# 在 line_bot.py 的 @handler.add(MessageEvent, message=TextMessage) 之前加入這段：

@handler.default()
def default(event):
    print(f"收到未處理事件: {event}")
    return
