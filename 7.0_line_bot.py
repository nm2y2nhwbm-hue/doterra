from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from handlers import get_drawing_response

app = Flask(__name__)

line_bot_api = LineBotApi('你的_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('你的_CHANNEL_SECRET')

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    
    if user_text == "抽牌":
        response_text = get_drawing_response(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_text)
        )

if __name__ == "__main__":
    app.run()
