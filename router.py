"""
無狀態路由模組（圖文選單三大按鈕專屬對接版）。
本系統全面對接「LINE 圖文選單（Rich Menu）」三大按鈕：
1. 【🪞 鏡子 1~5】
2. 【🌊 河流 6~10】
3. 【⛩️ 岔路 11~12】
當使用者在圖文選單點選任何一項（或在對話框輸入相關字樣）時，
立即回傳專屬的直跳卡片與專屬按鈕，保證 100% 可點擊跳轉至網頁中的對應分類！
"""

BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]
BLACKLIST_REPLY = (
    "【系統公告】\n本機器人暫不提供檔案轉檔／格式轉換服務。\n\n"
    "【快捷轉移區】\n如需轉檔工具，建議改用專門的線上轉檔服務。"
)

UNLOCK_KEYWORDS = ["🔑 6. 系統狀態與開發者指令", "解鎖密碼", "多特瑞精油卡牌抽卡程式"]
UNLOCK_REPLY = "🔓 系統狀態正常，歡迎點擊下方圖文選單開始抽卡。"

# 圖文選單三大按鈕關鍵字映射
CATEGORY_MAP = {
    "mirror": {
        "keywords": ["鏡子", "鏡", "1~5", "1-5", "15", "mirror"],
        "title": "鏡子 · 模式 1~5",
        "text": "🪞 照看你的此時此刻\n包含：今日能量、生活導引、三牌陣、了解自我、指示牌。\n\n請點擊下方按鈕開啟【鏡子】牌陣：",
        "button_label": "進入【鏡子】牌陣 (1~5) →",
    },
    "river": {
        "keywords": ["河流", "河", "6~10", "6-10", "610", "river"],
        "title": "河流 · 模式 6~10",
        "text": "🌊 陪伴你的時間流動\n包含：主題時間流、生命大運流年、流月、流日、年度軌跡。\n\n請點擊下方按鈕開啟【河流】牌陣：",
        "button_label": "進入【河流】牌陣 (6~10) →",
    },
    "crossroad": {
        "keywords": ["岔路", "岔", "11~12", "11-12", "1112", "crossroad"],
        "title": "岔路 · 模式 11~12",
        "text": "⛩️ 站在十字路口的香氣陪伴\n包含：二選一未來抉擇、三選一十字路口。\n\n請點擊下方按鈕開啟【岔路】牌陣：",
        "button_label": "進入【岔路】牌陣 (11~12) →",
    },
}


# 個別模式 1-5 關鍵字映射（相容舊版圖文選單直接送出模式名稱）
MODE_MAP = {
    1: {"keywords": ["今日能量", "單張心靈肯定小語", "單牌", "抽卡"], "title": "今日能量"},
    2: {"keywords": ["生活導引", "現階段狀態與方向指引", "兩張牌"], "title": "生活導引"},
    3: {"keywords": ["三牌陣", "身·心·靈", "身心靈", "三牌"], "title": "三牌陣"},
    4: {"keywords": ["了解自我", "別人眼中的你", "自我牌陣"], "title": "了解自我"},
    5: {"keywords": ["指示牌", "單一指示", "指定主題"], "title": "指示牌"},
}


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

    # 1. 優先偵測三大分類按鈕（【🪞 鏡子 1~5】、【🌊 河流 6~10】、【⛩️ 岔路 11~12】）
    for cat_key, cfg in CATEGORY_MAP.items():
        if _contains_any(text, cfg["keywords"]):
            return {
                "type": "category_redirect",
                "cat": cat_key,
                "title": cfg["title"],
                "text": cfg["text"],
                "button_label": cfg["button_label"],
            }

    # 2. 相容舊版圖文選單按鈕（今日能量、生活導引、三牌陣、了解自我、指示牌）
    for mode_id, cfg in MODE_MAP.items():
        if _contains_any(text, cfg["keywords"]):
            return {
                "type": "mode_redirect",
                "mode": f"mode_{mode_id}",
                "title": cfg["title"],
                "text": f"✦ {cfg['title']} ✦\n請點擊下方按鈕，進入牌陣為自己洗牌抽卡。",
                "button_label": f"進入「{cfg['title']}」牌陣 →",
            }

    # 3. 若使用者輸入任何其他文字，回傳全覽直跳大按鈕，絕不回傳純文字
    return {
        "type": "category_redirect",
        "cat": "mirror",
        "title": "雫之洞悉 · 線上抽卡",
        "text": "🌿 歡迎來到 雫之洞悉 · 返魂堂\n請點擊下方按鈕開啟線上心靈指引卡牌：",
        "button_label": "立即開啟線上卡牌 →",
    }


