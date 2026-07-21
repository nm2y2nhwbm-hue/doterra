import os
import sys
import traceback
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, TextSendMessage

import handlers

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

# --- 靜態檔案掛載 ---
# Flask 預設就會把 static_folder 掛在 static_url_path 底下，
# 這裡明確指定，確保未來 42 張精油洞悉卡圖片可用絕對路徑存取：
# https://你的網域/static/images/card_01.png
app = Flask(__name__, static_folder='static', static_url_path='/static')

# 初始化 API 與 Handler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# --- 觸發詞對應表 ---
# 判斷順序：黑名單 > 白名單 > 5 大抽卡模式
MODE_1_TRIGGERS = ["抽卡", "今日能量", "每日一牌"]
MODE_2_TRIGGERS = ["三牌陣", "身心靈"]
MODE_3_TRIGGERS = ["破局", "困擾"]
MODE_4_TRIGGERS = ["脈輪"]
MODE_5_TRIGGERS = ["開發者模式", "debug"]


# --- 路由區 ---
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


def _reply_text(reply_token, text):
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))


def _reply_flex_with_note(reply_token, flex_json, alt_text, note=None):
    """回傳一則 Flex Message，若有 note 則額外附加一則文字訊息（單次 reply 最多 5 則）"""
    messages = [FlexSendMessage(alt_text=alt_text, contents=flex_json)]
    if note:
        messages.append(TextSendMessage(text=note))
    line_bot_api.reply_message(reply_token, messages)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.strip()
    user_id = event.source.user_id
    reply_token = event.reply_token

    # 1. 黑名單：100% 後端硬攔截，優先於任何其他判斷
    blocked_reply = handlers.check_blacklist(msg)
    if blocked_reply:
        _reply_text(reply_token, blocked_reply)
        return

    # 2. 白名單：最高權限設定指令（放行，實際設定邏輯留待後續串接）
    if handlers.check_whitelist(msg):
        _reply_text(reply_token, "【權限驗證通過】已進入最高權限設定模式（設定邏輯待串接）。")
        return

    # 3. 模式1：今日能量指引
    if any(t in msg for t in MODE_1_TRIGGERS):
        flex, card, note = handlers.mode_1_daily_energy(user_id)
        if flex:
            _reply_flex_with_note(reply_token, flex, f"今日能量指引：{card['名稱']}", note)
        else:
            _reply_text(reply_token, note or "抽牌失敗，請稍後再試。")
        return

    # 4. 模式2：身心靈三牌陣
    if any(t in msg for t in MODE_2_TRIGGERS):
        flex, cards, note = handlers.mode_2_three_cards(user_id)
        if flex:
            line_bot_api.reply_message(reply_token, FlexSendMessage(alt_text="身心靈三牌陣", contents=flex))
        else:
            _reply_text(reply_token, note or "抽牌失敗，請稍後再試。")
        return

    # 5. 模式3：特定困擾破局牌
    if any(t in msg for t in MODE_3_TRIGGERS):
        flex, card, note = handlers.mode_3_issue_resolver(user_id, msg)
        if flex:
            _reply_flex_with_note(reply_token, flex, f"破局指引：{card['名稱']}", note)
        else:
            _reply_text(reply_token, note or "抽牌失敗，請稍後再試。")
        return

    # 6. 模式4：脈輪能量調和
    if any(t in msg for t in MODE_4_TRIGGERS):
        flex, card, note = handlers.mode_4_chakra_balance(user_id)
        if flex:
            _reply_flex_with_note(reply_token, flex, f"脈輪能量調和：{card['名稱']}", note)
        else:
            _reply_text(reply_token, note or "抽牌失敗，請稍後再試。")
        return

    # 7. 模式5：開發者後門測試模式
    if any(t in msg for t in MODE_5_TRIGGERS):
        _, _, report = handlers.mode_5_developer_debug()
        _reply_text(reply_token, report)
        return

    print(f"收到非觸發詞: {msg}")


# --- 啟動區 ---
if __name__ == "__main__":
    # 本地開發時自動啟用 debug 與固定 Port 5000，線上則使用預設
    is_debug = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
