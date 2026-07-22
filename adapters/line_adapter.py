"""
Adapter 層：把 router / card_engine 產出的通用 ActionResult
轉譯成 LINE 專屬的 SendMessage 物件。
"""
from linebot.models import TextSendMessage, FlexSendMessage


def _build_bubble(card: dict, label: str = None) -> dict:
    header_contents = []
    if label:
        header_contents.append({"type": "text", "text": label,
                                 "size": "xs", "color": "#B08968", "align": "center"})
    header_contents += [
        {"type": "text", "text": card.get("name", "未知"),
         "weight": "bold", "size": "xl", "align": "center"},
        {"type": "text", "text": card.get("name_en", ""),
         "size": "sm", "align": "center", "color": "#888888"},
    ]
    return {
        "type": "bubble",
        "header": {"type": "box", "layout": "vertical", "contents": header_contents},
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
    if not action_result:
        return None

    kind = action_result.get("type")

    if kind == "text":
        return TextSendMessage(text=action_result.get("text", ""))

    if kind == "flex_single":
        card = action_result.get("card")
        if not card:
            return TextSendMessage(text="目前查無卡牌資料。")
        return FlexSendMessage(alt_text=f"你抽到了 {card.get('name')}",
                                contents=_build_bubble(card))

    if kind == "flex_positions":
        positions = action_result.get("positions", [])
        if not positions:
            return TextSendMessage(text="目前查無卡牌資料。")
        bubbles = [_build_bubble(p["card"], label=p["label"]) for p in positions]
        carousel = {"type": "carousel", "contents": bubbles}
        alt = "、".join(p["card"].get("name", "") for p in positions)
        return FlexSendMessage(alt_text=f"牌陣結果：{alt}", contents=carousel)

    return TextSendMessage(text="系統發生未知錯誤，請聯絡管理員。")
