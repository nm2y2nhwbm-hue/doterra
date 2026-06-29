from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_oil_flex_message

app = Flask(__name__)

# 使用你原本的金鑰
line_bot_api = LineBotApi('4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('eea492cdcc8c24ddc585e72367ec86fd')

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
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔮 系統迷路中，請確認資料庫狀態。"))

if __name__ == "__main__":
    app.run(port=5000)
