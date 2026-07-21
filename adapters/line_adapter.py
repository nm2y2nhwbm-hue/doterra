"""
Adapter 層：把 router / card_engine 產出的通用 ActionResult
轉譯成 LINE 專屬的 SendMessage 物件。
未來若要加 Discord，只需新增 adapters/discord_adapter.py，
core/ 與 router.py 完全不用改。
"""
from linebot.models import TextSendMessage, FlexSendMessage


def _build_bubble(card: dict) -> dict:
    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": card.get("name", "未知"),
                 "weight": "bold", "size": "xl", "align": "center"},
                {"type": "text", "text": card.get("name_en", ""),
                 "size": "sm", "align": "center", "color": "#888888"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "image", "url": card.get("image_url"),
                 "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{card.get('keywords', '無')}",
                 "margin": "md", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": card.get("guidance", "無"),
                 "wrap": True, "margin": "md", "size": "sm"},
            ],
        },
    }


def to_line_message(action_result: dict):
    """action_result 為 None 時回傳 None，通訊外殼可選擇不回應。"""
    if not action_result:
        return None

    kind = action_result.get("type")

    if kind == "text":
        return TextSendMessage(text=action_result.get("text", ""))

    if kind == "flex_card":
        card = action_result.get("card")
        if not card:
            return TextSendMessage(text="目前查無卡牌資料。")
        bubble = _build_bubble(card)
        return FlexSendMessage(alt_text=f"你抽到了 {card.get('name')}", contents=bubble)

    if kind == "flex_carousel":
        cards = action_result.get("cards", [])
        if not cards:
            return TextSendMessage(text="目前查無卡牌資料。")
        carousel = {"type": "carousel", "contents": [_build_bubble(c) for c in cards]}
        alt = "、".join(c.get("name", "") for c in cards)
        return FlexSendMessage(alt_text=f"三牌陣：{alt}", contents=carousel)

    return TextSendMessage(text="系統發生未知錯誤，請聯絡管理員。")