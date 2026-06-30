import os
import csv
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_drawing_response

# 1. 檢查環境變數是否設定
# 這些變數請去 Render Dashboard 的 Environment 設定
CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    print("錯誤：請在 Render 的 Environment 中設定 CHANNEL_ACCESS_TOKEN 與 CHANNEL_SECRET")
    sys.exit(1) # 強制停止，這樣你能在 Logs 看到這行錯誤

app = Flask(__name__)

LineBotApi('4mTLI9JKpQXu/0Kb2qeqiOHQfjv7WFhnYpu21FG0Y8E8ob1q0YjUEc+GrtqfBZxqJQ8DoSBh+fLKPtx1zNoUHaem8j+ATxGJ9E1gpZF7UidCgSn4fAJ2WcimDRs7dZepx2m+fe1KTs6PIDZyGEtZ7AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('eea492cdcc8c24ddc585e72367ec86fd')


import traceback # 在檔案最上方加入這行

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature', '')
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("--- 發生錯誤啦！ ---")
        traceback.print_exc() # 這行會印出完整的錯誤堆疊，包含哪一行出錯
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    print(f"收到訊息: {msg}")  # 這行會把收到的內容印在 Logs 裡
    
    if "抽牌" in msg:
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        if flex_json:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
            )
        else:
            print("取得資料失敗或無資料")
    else:
        print(f"訊息不符合觸發條件: {msg}")

if __name__ == "__main__":
    app.run()
# trigger deployment
# 在 line_bot.py 的 @handler.add(MessageEvent, message=TextMessage) 之前加入這段：

@handler.default()
def default(event):
    print(f"收到未處理事件: {event}")
    return
