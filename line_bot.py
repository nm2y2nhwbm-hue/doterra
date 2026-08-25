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

# CORS：同時允許 Render 本身與 Vercel 網域呼叫 API，
# 避免因為之後測試網址在兩邊之間切換而被擋。
CORS(app, resources={r"/api/*": {"origins": [
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


@app.route("/health", methods=['GET'])
def health():
    return {"status": "ok"}


@app.route("/api/oils", methods=['GET'])
def api_oils():
    """回傳 69 張精油卡的完整 JSON，供一頁式前端讀取。"""
    return jsonify(db.fetch_oils_data())


@app.route("/api/indicators", methods=['GET'])
def api_indicators():
    """回傳 12 張指示卡的完整 JSON，供模式 5 前端讀取。"""
    return jsonify(db.fetch_indicator_cards())


@app.route("/api/log-draw", methods=['POST'])
def api_log_draw():
    """
    前端抽卡完成後呼叫，記錄「誰、何時、抽了哪個牌陣、抽到哪些卡」。
    請求格式：{ "user_id": "...", "display_name": "...", "mode": "mode_1", "cards": ["檸檬", "玫瑰"] }
    """
    data = request.get_json(silent=True) or {}
    ok = draw_logger.log_draw(
        user_id=data.get('user_id', ''),
        display_name=data.get('display_name', ''),
        mode=data.get('mode', ''),
        card_names=data.get('cards', []),
    )
    return jsonify({"success": ok})


def _no_store_json(payload, status=200):
    response = jsonify(payload)
    response.status_code = status
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    return response


def _handoff_error_response(error):
    return _no_store_json({
        "persisted": False,
        "error": error.public_message,
    }, error.status_code)


def _request_client_ip():
    forwarded_for = request.headers.get('X-Forwarded-For', '')
    if forwarded_for:
        client_ip = forwarded_for.split(',', 1)[0].strip()
        if client_ip:
            return client_ip[:64]
    return (request.remote_addr or '')[:64]


@app.route("/api/draws/health", methods=['GET'])
def api_draws_health():
    payload, status = experience_handoff.get_readiness()
    return _no_store_json(payload, status)


@app.route("/api/draws", methods=['POST'])
def api_create_draw():
    data = request.get_json(silent=True) or {}
    try:
        fingerprint = experience_handoff.build_request_fingerprint(
            _request_client_ip(),
            request.headers.get('User-Agent', ''),
        )
        result = experience_handoff.create_draw(data, fingerprint)
        return _no_store_json(result)
    except experience_handoff.HandoffError as error:
        return _handoff_error_response(error)


@app.route("/api/draws/redeem", methods=['POST'])
def api_redeem_draw():
    data = request.get_json(silent=True) or {}
    try:
        result = experience_handoff.redeem_draw(data)
        return _no_store_json(result)
    except experience_handoff.HandoffError as error:
        return _handoff_error_response(error)


if __name__ == "__main__":
    is_debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
