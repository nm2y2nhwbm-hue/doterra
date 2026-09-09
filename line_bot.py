import os
import sys
import traceback
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage

from router import route_message
from adapters.line_adapter import to_line_message
from core import database_manager as db
from core import draw_logger
from core import experience_handoff

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
    print("錯誤：無法取得 CHANNEL_ACCESS_TOKEN 或 CHANNEL_SECRET。")
    print("請確認線上平台設定或本地 .env 檔案內容。")
    sys.exit(1)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024

# CORS：同時允許 Render 本身與 Vercel 網域呼叫 API 與 Health 探測端點，
# 避免因為之後測試網址在兩邊之間切換而被擋。
CORS(app, resources={r"/*": {"origins": [
    "https://doterra-two.vercel.app",
    "https://doterra-73pv.onrender.com",
]}})

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers.get('X-Line-Signature', '')
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception:
        traceback.print_exc()
        abort(500)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    action_result = route_message(user_id, text)

    if action_result is None:
        print(f"[line_bot] 收到非觸發詞: {text}")
        return

    reply = to_line_message(action_result)
    if reply is None:
        return

    line_bot_api.reply_message(event.reply_token, reply)


# 註冊 Agent 1 的後端 API 藍圖模組
from api import api_bp
app.register_blueprint(api_bp)


if __name__ == "__main__":
    is_debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
