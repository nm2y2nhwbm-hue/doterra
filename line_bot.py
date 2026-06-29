import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_drawing_response

app = Flask(__name__)

# 從環境變數讀取 (這些變數要在 Render 的 Dashboard 設定)
line_bot_api = LineBotApi(os.environ.get('4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU='))
handler = WebhookHandler(os.environ.get('eea492cdcc8c24ddc585e72367ec86fd'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "抽牌":
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        # 增加保護：確認 oil_data 存在才發送
        if oil_data:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
            )

if __name__ == "__main__":
    app.run()
