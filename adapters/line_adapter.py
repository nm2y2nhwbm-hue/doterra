"""
Adapter 層（V2：純導流版）。
LINE 端不再組裝完整卡片結果，只負責把 router.py 的 mode_redirect
轉譯成一句導流文字 + 一顆 LIFF 按鈕。真正的抽卡結果卡片，
由前端 static/cards.html 抽完後透過 liff.sendMessages() 自己送回聊天室。
"""
import os
from linebot.models import TextSendMessage, FlexSendMessage

LIFF_ID = os.environ.get('LIFF_ID', '2010916161-HrIOEAda')  # 雫之洞悉・返魂堂（開發環境）


def _build_redirect_bubble(action_result: dict) -> dict:
    mode = action_result.get("mode", "")
    mode_num = mode.replace('mode_', '') if mode else ""
    cat = action_result.get("cat", "")
    title = action_result.get("title", "")
    text = action_result.get("text", "")
    button_label = action_result.get("button_label") or f"進入「{title}」"

    if cat:
        uri = f"https://miniapp.line.me/{LIFF_ID}?cat={cat}"
    elif mode_num:
        uri = f"https://miniapp.line.me/{LIFF_ID}?mode={mode_num}"
    else:
        uri = f"https://miniapp.line.me/{LIFF_ID}"

    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": f"✦ {title} ✦", "weight": "bold",
                 "size": "lg", "align": "center", "color": "#2D4232"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": text, "wrap": True, "margin": "md",
                 "size": "sm", "color": "#4A3F35"},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#355343",
                    "action": {
                        "type": "uri",
                        "label": button_label,
                        "uri": uri,
                    },
                },
            ],
        },
    }


def to_line_message(action_result: dict):
    if not action_result:
        return None

    kind = action_result.get("type")

    if kind == "text":
        return TextSendMessage(text=action_result.get("text", ""))

    if kind in ("mode_redirect", "category_redirect"):
        title = action_result.get("title", "")
        bubble = _build_redirect_bubble(action_result)
        return FlexSendMessage(alt_text=f"點擊進入「{title}」", contents=bubble)

    return TextSendMessage(text="系統發生未知錯誤，請聯絡管理員。")
