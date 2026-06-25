from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from handlers import get_drawing_response
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
    if any(k in event.message.text for k in ["抽牌", "抽卡", "draw"]):
        reply = get_drawing_response()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run(port=int(os.environ.get('PORT', 5000)))