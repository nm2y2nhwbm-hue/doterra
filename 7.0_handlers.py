from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
from handlers import get_drawing_response

# 初始化
line_bot_api = LineBotApi('你的_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('你的_CHANNEL_SECRET')

def handle_message(event):
    if event.message.text == "抽牌":
        # 取得文字回覆
        response_text, oil_data = get_drawing_response(event.source.user_id)
        
        # 發送純文字訊息
        message = TextSendMessage(text=response_text)
        line_bot_api.reply_message(event.reply_token, message)