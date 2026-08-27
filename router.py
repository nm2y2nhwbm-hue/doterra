"""
無狀態路由模組（V2：純導流版）。
每一句訊息獨立判定，不參考任何上一句對話狀態。
順位：1 黑名單攔截 → 2 白名單解鎖 → 3 12大牌陣導流（回一句話 + LIFF 按鈕）→ 4 牌陣總導覽。
實際抽卡邏輯全部在 static/cards.html 前端完成。
"""
from core import card_engine as engine

BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]
BLACKLIST_REPLY = (
    "【系統公告】\n本機器人暫不提供檔案轉檔／格式轉換服務。\n\n"
    "【快捷轉移區】\n如需轉檔工具，建議改用專門的線上轉檔服務。"
)

UNLOCK_KEYWORDS = ["🔑 6. 系統狀態與開發者指令", "解鎖密碼", "多特瑞精油卡牌抽卡程式"]
UNLOCK_REPLY = "🔓 系統狀態正常，歡迎隨時開始新的一場占卜。"

MODE_TITLES = {
    1: "今日能量",
    2: "生活導引",
    3: "三牌陣",
    4: "了解自我",
    5: "指示牌",
    6: "主題時間流",
    7: "生命大運流年・看流年",
    8: "生命大運流年・看流月",
    9: "生命大運流年・看流日",
    10: "年度生命軌跡",
    11: "二選一未來抉擇",
    12: "三選一十字路口",
}

MODE_KEYWORDS = {
    1: ["1", "01", "１", "今日能量", "單張心靈肯定小語", "單牌", "抽卡"],
    2: ["2", "02", "２", "生活導引", "現階段狀態與方向指引", "兩張牌"],
    3: ["3", "03", "３", "三牌陣", "身·心·靈", "身心靈", "三牌"],
    4: ["4", "04", "４", "了解自我", "別人眼中的你與真正的你", "自我牌陣"],
    5: ["5", "05", "５", "指示牌", "單一指示牌與精油對應占卜", "指定主題"],
    6: ["6", "06", "６", "主題時間流", "時間流"],
    7: ["7", "07", "７", "看流年", "流年", "生命大運流年"],
    8: ["8", "08", "８", "看流月", "流月"],
    9: ["9", "09", "９", "看流日", "流日"],
    10: ["10", "１０", "年度生命軌跡", "生命軌跡"],
    11: ["11", "１１", "二選一未來抉擇", "二選一", "抉擇"],
    12: ["12", "１２", "三選一十字路口", "三選一", "十字路口"],
}

INDICATOR_SYMBOLS = engine._get_indicator_symbols()


def _contains_any(text: str, keywords) -> bool:
    return any(kw in text for kw in keywords)


def _match_exact_or_contains(text: str, keywords) -> bool:
    t_clean = text.strip()
    digits = "０１２３４５６７８９"
    for kw in keywords:
        if kw.isdigit() or (len(kw) <= 2 and any(d in kw for d in digits)):
            if t_clean == kw:
                return True
        elif kw in t_clean:
            return True
    return False


def _extract_indicator(text: str):
    return next((s for s in INDICATOR_SYMBOLS if s in text), None)


def _build_mode_redirect(mode_id: int) -> dict:
    return {
        "type": "mode_redirect",
        "mode": f"mode_{mode_id}",
        "title": MODE_TITLES[mode_id],
        "text": f"✦ {MODE_TITLES[mode_id]} ✦\n請點擊下方按鈕，進入牌陣為自己洗牌抽卡。",
    }


def _build_general_welcome() -> dict:
    return {
        "type": "mode_redirect",
        "mode": "mode_1",
        "title": "雫之洞悉 · 牌陣總導覽",
        "text": "🌿 歡迎來到 雫之洞悉 · 返魂堂\n\n您可以點擊下方選單開啟抽卡，或輸入數字 1～12 直接開啟專屬牌陣：\n\n🪞 鏡子系列：1 今日能量、2 生活導引、3 三牌陣、4 了解自我、5 指示牌\n🌊 河流系列：6 主題時間流、7 看流年、8 看流月、9 看流日、10 年度軌跡\n⛩️ 岔路系列：11 二選一抉擇、12 三選一十字路口",
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
    if indicator or _match_exact_or_contains(text, MODE_KEYWORDS[5]):
        return _build_mode_redirect(5)

    for mode_id in (12, 11, 10, 9, 8, 7, 6, 4, 3, 2, 1):
        if _match_exact_or_contains(text, MODE_KEYWORDS[mode_id]):
            return _build_mode_redirect(mode_id)

    return _build_general_welcome()

