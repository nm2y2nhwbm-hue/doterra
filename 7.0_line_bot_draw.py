from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import FlexSendMessage, TextSendMessage
from handlers import get_drawing_response

app = Flask(__name__)
line_bot_api = LineBotApi('eea492cdcc8c24ddc585e72367ec86fd')
handler = WebhookHandler('4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU=')

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