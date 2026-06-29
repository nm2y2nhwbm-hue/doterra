from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage
from handlers import get_drawing_response

# 初始化
line_bot_api = LineBotApi('你的_eea492cdcc8c24ddc585e72367ec86fd')
handler = WebhookHandler('你的_4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU=')

def handle_message(event):
    if event.message.text == "抽牌":
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        
        # 將產生的 JSON 封裝為 FlexSendMessage
        message = FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
        
        line_bot_api.reply_message(event.reply_token, message)