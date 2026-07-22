"""
Adapter 層：把 router / card_engine 產出的通用 ActionResult
轉譯成 LINE 專屬的 Flex Message JSON 結構。
"""
import os
from linebot.models import TextSendMessage, FlexSendMessage

# 底部按鈕連結，未設定時退回安全預設值
SHOP_URL = os.environ.get('SHOP_URL', 'https://example.com/shop')
BASE_URL = os.environ.get('BASE_URL', 'https://example.com')


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
        "hero": {
            "type": "image",
            "url": card.get("image_url"),
            "size": "full",
            "aspectRatio": "4:3",
            "aspectMode": "cover",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": "脈輪", "size": "xs", "color": "#B08968", "flex": 1},
                        {"type": "text", "text": card.get("chakra", "無"), "size": "sm",
                         "color": "#555555", "flex": 4, "wrap": True},
                    ],
                },
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": "關鍵詞", "size": "xs", "color": "#B08968", "flex": 1},
                        {"type": "text", "text": card.get("keywords", "無"), "size": "sm",
                         "color": "#555555", "flex": 4, "wrap": True},
                    ],
                },
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": card.get("guidance", "無"),
                 "wrap": True, "margin": "md", "size": "sm", "color": "#333333"},
            ],
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "看完整解析",
                        "uri": f"{BASE_URL}/oil/{card.get('id', '')}",
                    },
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#B08968",
                    "action": {
                        "type": "uri",
                        "label": "前往專屬商城",
                        "uri": SHOP_URL,
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
