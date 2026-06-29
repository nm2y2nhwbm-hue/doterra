from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from handlers import get_drawing_response

# 填入你的 Token
line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

def handle_message(event):
    if event.message.text == "抽牌":
        text_reply, oil = get_drawing_response(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text_reply)
        )