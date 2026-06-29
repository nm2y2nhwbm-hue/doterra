from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_drawing_response

app = Flask(__name__)

line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('YOUR_CHANNEL_SECRET')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK' # 確保這裡盡快回傳 200 OK

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "抽牌":
        # 取得 flex_json 與資料
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        # 發送訊息
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
        )

if __name__ == "__main__":
    app.run()
