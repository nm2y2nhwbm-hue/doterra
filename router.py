"""
無狀態路由模組（純圖文選單唯一方案）。
本系統全面採用「LINE 圖文選單（Rich Menu）」作為唯一抽卡入口。
徹底移除任何「輸入數字」抽卡邏輯。
若收到使用者輸入文字，一律溫柔引導使用螢幕下方圖文選單。
"""

BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]
BLACKLIST_REPLY = (
    "【系統公告】\n本機器人暫不提供檔案轉檔／格式轉換服務。\n\n"
    "【快捷轉移區】\n如需轉檔工具，建議改用專門的線上轉檔服務。"
)

UNLOCK_KEYWORDS = ["🔑 6. 系統狀態與開發者指令", "解鎖密碼", "多特瑞精油卡牌抽卡程式"]
UNLOCK_REPLY = "🔓 系統狀態正常，歡迎點擊下方圖文選單開始抽卡。"

GUIDE_REPLY = (
    "🌿 歡迎來到 雫之洞悉 · 返魂堂\n\n"
    "請點擊螢幕下方的【圖文選單】，即可開啟線上心靈指引卡牌。"
)


def _contains_any(text: str, keywords) -> bool:
    return any(kw in text for kw in keywords)


def route_message(user_id: str, text: str):
    text = (text or "").strip()
    if not text:
        return None

    if _contains_any(text, BLACKLIST_KEYWORDS):
        return {"type": "text", "text": BLACKLIST_REPLY}

    if _contains_any(text, UNLOCK_KEYWORDS):
        return {"type": "text", "text": UNLOCK_REPLY}

    # 純圖文選單架構：一律引導點擊下方選單
    return {"type": "text", "text": GUIDE_REPLY}


