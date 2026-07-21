"""
無狀態路由模組。
每一句訊息獨立判定，絕不參考任何「上一句對話」的狀態機。
判定順序焊死如下（由上而下，一旦命中立刻回傳，不再往下判斷）：
  順位 1：黑名單攔截（100% 後端硬攔截，不驚動任何商業邏輯 / AI）
  順位 2：白名單解鎖
  順位 3：5 大模式獨立觸發分流
"""
from core import memory_manager as mem
from core import card_engine as engine

# ---------- 順位 1：黑名單攔截 ----------
BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]
BLACKLIST_REPLY = (
    "【系統公告】\n"
    "本機器人暫不提供檔案轉檔／格式轉換服務。\n\n"
    "【快捷轉移區】\n"
    "如需轉檔工具，建議改用專門的線上轉檔服務。"
)

# ---------- 順位 2：白名單解鎖 ----------
UNLOCK_KEYWORDS = ["解鎖密碼", "多特瑞精油卡牌抽卡程式"]
UNLOCK_REPLY = "🔓 今日能量鎖定已解除，你可以重新抽取今日能量卡牌。"

# ---------- 順位 3：5 大模式關鍵字 ----------
MODE_1_KEYWORDS = ["今日能量", "抽牌", "抽卡"]
MODE_2_KEYWORDS = ["三牌陣", "三張牌"]
MODE_3_KEYWORDS = ["困擾破局", "困擾", "煩惱"]
MODE_4_KEYWORDS = ["脈輪"]
MODE_5_KEYWORDS = ["debug", "系統報告", "系統偵錯"]

CHAKRA_LIST = ["海底輪", "生殖輪", "太陽神經叢", "心輪", "喉輪", "眉心輪", "頂輪"]


def _contains_any(text: str, keywords) -> bool:
    return any(kw in text for kw in keywords)


def route_message(user_id: str, text: str):
    """
    回傳通用 ActionResult dict（或 None 代表無匹配，通訊外殼可自行決定要不要回話）。
    這個函式完全不認識 LINE / Discord，只吃字串、吐資料。
    """
    text = (text or "").strip()
    if not text:
        return None

    # 順位 1：黑名單攔截
    if _contains_any(text, BLACKLIST_KEYWORDS):
        return {"type": "text", "text": BLACKLIST_REPLY}

    # 順位 2：白名單解鎖
    if _contains_any(text, UNLOCK_KEYWORDS):
        mem.clear_today_lock(user_id)
        return {"type": "text", "text": UNLOCK_REPLY}

    # 順位 3：5 大模式分流（模式間互斥判斷順序：脈輪 > debug > 三牌陣 > 困擾破局 > 今日能量）
    if _contains_any(text, MODE_4_KEYWORDS):
        chakra = next((c for c in CHAKRA_LIST if c in text), None)
        if chakra:
            return engine.mode_4_chakra_pick(user_id, chakra)
        return {"type": "text", "text": "請指定脈輪類別，例如：心輪、喉輪、頂輪…"}

    if _contains_any(text, MODE_5_KEYWORDS):
        return engine.mode_5_debug_report(user_id)

    if _contains_any(text, MODE_2_KEYWORDS):
        return engine.mode_2_three_card_spread(user_id)

    if _contains_any(text, MODE_3_KEYWORDS):
        return engine.mode_3_breakthrough(user_id, user_question=text)

    if _contains_any(text, MODE_1_KEYWORDS):
        return engine.mode_1_today_energy(user_id)

    return None