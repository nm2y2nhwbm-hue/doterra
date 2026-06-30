import os
import sys
import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
from handlers import get_drawing_response

# --- 環境設定區 (二合一處理) ---
# 只有在本地執行時，才嘗試載入 .env
if os.path.exists(".env"):
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("已偵測到 .env 檔案，正在載入環境變數...")
    except ImportError:
        print("未安裝 python-dotenv，將直接使用系統環境變數。")

CHANNEL_ACCESS_TOKEN = os.environ.get('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.environ.get('CHANNEL_SECRET')

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    # 這段訊息適應兩種環境：Render 會看此處，本地則方便除錯
    print("錯誤：無法取得 CHANNEL_ACCESS_TOKEN 或 CHANNEL_SECRET。")
    print("請確認線上平台設定或本地 .env 檔案內容。")
    sys.exit(1)

app = Flask(__name__)

# 初始化 API 與 Handler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# --- 路由區 ---
@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature', '')
    try:
        handler.handle(body, signature)
    except Exception:
        traceback.print_exc()
        abort(500)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if "抽牌" in msg:
        flex_json, oil_data = get_drawing_response(event.source.user_id)
        if flex_json and oil_data:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=f"你抽到了 {oil_data['名稱']}", contents=flex_json)
            )
    else:
        print(f"收到非觸發詞: {msg}")

# --- 啟動區 ---
if __name__ == "__main__":
    # 本地開發時自動啟用 debug 與固定 Port 5000，線上則使用預設
    is_debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
