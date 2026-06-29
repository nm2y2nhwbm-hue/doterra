import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage
from handlers import get_drawing_response

app = Flask(__name__)

# 使用 os.environ 從 Render 環境變數中讀取，這是最安全且正確的做法
LineBotApi('4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('eea492cdcc8c24ddc585e72367ec86fd')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if "抽牌" in event.message.text:
        # 呼叫邏輯取得 Flex 資料
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        
        if flex_json:
            message = FlexSendMessage(alt_text=f"你抽到了 {oil_data.get('名稱', '精油')}", contents=flex_json)
            line_bot_api.reply_message(event.reply_token, message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="🔮 系統迷路中，請確認資料庫狀態。"))

if __name__ == "__main__":
    app.run()
