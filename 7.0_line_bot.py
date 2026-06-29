from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_oil_flex_message

app = Flask(__name__)
line_bot_api = LineBotApi('你的_ACCESS_TOKEN')
handler = WebhookHandler('你的_CHANNEL_SECRET')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if "抽牌" in event.message.text:
        flex_json, name = get_oil_flex_message()
        if flex_json:
            message = FlexSendMessage(alt_text=f"今日指引：{name}", contents=flex_json)
            line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    app.run(port=5000)
