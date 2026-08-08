"""
無狀態路由模組（V2：純導流版）。
每一句訊息獨立判定，不參考任何上一句對話狀態。
順位：1 黑名單攔截 → 2 白名單解鎖 → 3 五大牌陣導流（回一句話 + LIFF 按鈕）。
實際抽卡邏輯全部在 static/cards.html 前端完成，本檔案不再呼叫任何抽卡函式。
"""
from core import card_engine as engine

BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]
BLACKLIST_REPLY = (
    "【系統公告】\n本機器人暫不提供檔案轉檔／格式轉換服務。\n\n"
    "【快捷轉移區】\n如需轉檔工具，建議改用專門的線上轉檔服務。"
)

UNLOCK_KEYWORDS = ["🔑 6. 系統狀態與開發者指令", "解鎖密碼", "多特瑞精油卡牌抽卡程式"]
UNLOCK_REPLY = "🔓 系統狀態正常，歡迎隨時開始新的一場占卜。"

MODE_KEYWORDS = {
    1: ["🔮 1. 單張心靈肯定小語", "今日能量", "抽卡", "單牌"],
    2: ["💫 2. 現階段狀態與方向指引", "生活導引", "兩張牌", "導引牌陣"],
    3: ["🌿 3. 身·心·靈全方位深度解析", "三牌陣", "身心靈", "三牌"],
    4: ["🧘 4. 別人眼中的你與真正的你", "了解自我", "自我牌陣"],
    5: ["🎯 5. 單一指示牌與精油對應占卜", "指示牌", "單一指示", "指定主題"],
}

MODE_TITLES = {
    1: "今日能量",
    2: "生活導引",
    3: "三牌陣",
    4: "了解自我",
    5: "指示牌",
}

INDICATOR_SYMBOLS = engine._get_indicator_symbols()


def _contains_any(text: str, keywords) -> bool:
    return any(kw in text for kw in keywords)


def _extract_indicator(text: str):
    return next((s for s in INDICATOR_SYMBOLS if s in text), None)


def _build_mode_redirect(mode_id: int) -> dict:
    return {
        "type": "mode_redirect",
        "mode": f"mode_{mode_id}",
        "title": MODE_TITLES[mode_id],
        "text": f"✦ {MODE_TITLES[mode_id]} ✦\n請點擊下方按鈕，進入牌陣為自己洗牌抽卡。",
    }


def route_message(user_id: str, text: str):
    text = (text or "").strip()
    if not text:
        return None

    if _contains_any(text, BLACKLIST_KEYWORDS):
        return {"type": "text", "text": BLACKLIST_REPLY}

    if _contains_any(text, UNLOCK_KEYWORDS):
        return {"type": "text", "text": UNLOCK_REPLY}

    indicator = _extract_indicator(text)
    if indicator or _contains_any(text, MODE_KEYWORDS[5]):
        return _build_mode_redirect(5)

    for mode_id in (4, 3, 2, 1):
        if _contains_any(text, MODE_KEYWORDS[mode_id]):
            return _build_mode_redirect(mode_id)

    return None
