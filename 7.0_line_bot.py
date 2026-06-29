import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from handlers import get_drawing_response

app = Flask(__name__)

# --- 修正處：直接填入字串，不要用 os.environ.get ---
# 如果你有設定環境變數，請改為 os.environ.get('CHANNEL_ACCESS_TOKEN')
# 但為了快速排除故障，建議先直接貼上字串測試
LINE_CHANNEL_ACCESS_TOKEN = '4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'eea492cdcc8c24ddc585e72367ec86fd'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

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
