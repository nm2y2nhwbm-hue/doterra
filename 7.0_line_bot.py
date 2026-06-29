from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage
from handlers import get_drawing_response

# 初始化
line_bot_api = LineBotApi('')
handler = WebhookHandler('')

def handle_message(event):
    if event.message.text == "抽牌":
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        
        # 將產生的 JSON 封裝為 FlexSendMessage
        message = FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
        
        line_bot_api.reply_message(event.reply_token, message)
