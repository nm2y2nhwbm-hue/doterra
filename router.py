"""
無狀態路由模組。每一句訊息獨立判定，不參考任何上一句對話狀態。
順位：1 黑名單攔截 → 2 白名單解鎖 → 3 五大牌陣模式分流。
觸發字同時保留「Rich Menu 實際送出文字」與舊版口語關鍵字，兩者並存。
"""
from core import memory_manager as mem
from core import card_engine as engine

BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]
BLACKLIST_REPLY = (
    "【系統公告】\n本機器人暫不提供檔案轉檔／格式轉換服務。\n\n"
    "【快捷轉移區】\n如需轉檔工具，建議改用專門的線上轉檔服務。"
)

UNLOCK_KEYWORDS = ["🔑 6. 系統狀態與開發者指令", "解鎖密碼", "多特瑞精油卡牌抽卡程式"]
UNLOCK_REPLY = "🔓 今日能量鎖定已解除，你可以重新抽取今日能量卡牌。"

MODE_1_KEYWORDS = ["🔮 1. 單張心靈肯定小語", "今日能量", "抽卡", "單牌"]
MODE_2_KEYWORDS = ["💫 2. 現階段狀態與方向指引", "生活導引", "兩張牌", "導引牌陣"]
MODE_3_KEYWORDS = ["🌿 3. 身·心·靈全方位深度解析", "三牌陣", "身心靈", "三牌"]
MODE_4_KEYWORDS = ["🧘 4. 別人眼中的你與真正的你", "了解自我", "自我牌陣"]
MODE_5_KEYWORDS = ["🎯 5. 單一指示牌與精油對應占卜", "指示牌", "單一指示", "指定主題"]

INDICATOR_SYMBOLS = engine._get_indicator_symbols()


def _contains_any(text: str, keywords) -> bool:
    return any(kw in text for kw in keywords)


def _extract_indicator(text: str):
    return next((s for s in INDICATOR_SYMBOLS if s in text), None)


def route_message(user_id: str, text: str):
    text = (text or "").strip()
    if not text:
        return None

    if _contains_any(text, BLACKLIST_KEYWORDS):
        return {"type": "text", "text": BLACKLIST_REPLY}

    if _contains_any(text, UNLOCK_KEYWORDS):
        mem.clear_today_lock(user_id)
        return {"type": "text", "text": UNLOCK_REPLY}

    indicator = _extract_indicator(text)
    if indicator or _contains_any(text, MODE_5_KEYWORDS):
        if not indicator:
            return engine.mode_5_prompt_for_indicator()
        return engine.mode_5_indicator_spread(user_id, indicator)

    if _contains_any(text, MODE_4_KEYWORDS):
        return engine.mode_4_self_awareness(user_id)

    if _contains_any(text, MODE_3_KEYWORDS):
        return engine.mode_3_body_mind_spirit(user_id)

    if _contains_any(text, MODE_2_KEYWORDS):
        return engine.mode_2_life_guidance(user_id)

    if _contains_any(text, MODE_1_KEYWORDS):
        return engine.mode_1_today_energy(user_id)

    return None
