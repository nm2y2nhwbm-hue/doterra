from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from handlers import get_drawing_response, get_followup_response, get_menu_message
import os

app = Flask(__name__)
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id 
    user_text = event.message.text
    
    # 觸發選單
    if "選單" in user_text:
        line_bot_api.reply_message(event.reply_token, get_menu_message())
        
    # 根據選單點擊結果分流 (1張, 2張, 3張)
    elif "抽牌" in user_text:
        count = 1
        if "引導" in user_text: count = 2
        elif "療育" in user_text: count = 3
        
        reply, _ = get_drawing_response(user_id, count=count)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            
    elif any(k in user_text for k in ["解釋", "更多"]):
        reply = get_followup_response(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))