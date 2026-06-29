from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage, TextSendMessage
from handlers import get_drawing_response

app = Flask(__name__)
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "抽牌":
        flex_json, _ = get_drawing_response(event.source.user_id)
        if flex_json:
            # 將 JSON 轉為 FlexSendMessage 發送
            message = FlexSendMessage(alt_text="你的精油洞悉卡", contents=flex_json)
            line_bot_api.reply_message(event.reply_token, message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="抽牌失敗..."))

if __name__ == "__main__":
    app.run()