import random

from database_manager import (
    fetch_oils_data,
    get_locked_card,
    lock_today_card,
    is_locked_today,
    debug_memory_snapshot,
)

# ==================================================================
# 防禦牆：白名單 / 黑名單
# ==================================================================

# 白名單：命中即視為最高權限，放行設定指令（實際設定邏輯留待後續串接）
WHITELIST_KEYWORDS = ["解鎖密碼", "多特瑞精油卡牌抽卡程式"]

# 黑名單：命中即 100% 後端硬攔截，不執行任何任務
BLACKLIST_KEYWORDS = ["轉檔", "格式轉換"]

BLACKLIST_REPLY = (
    "【系統公告】\n"
    "此項功能不在本服務提供範圍內，已由後端攔截。\n\n"
    "【快捷轉移區】\n"
    "請直接輸入「抽卡」開始今日的能量指引占卜。"
)


def check_whitelist(text: str) -> bool:
    """是否命中白名單關鍵字（最高權限指令）"""
    return any(keyword in text for keyword in WHITELIST_KEYWORDS)


def check_blacklist(text: str):
    """
    是否命中黑名單關鍵字。
    命中回傳固定攔截文字（str），未命中回傳 None。
    """
    if any(keyword in text for keyword in BLACKLIST_KEYWORDS):
        return BLACKLIST_REPLY
    return None


# ==================================================================
# Flex Message 建構工具
# ==================================================================

def build_flex_bubble(card: dict, title_prefix: str = "") -> dict:
    """把一張卡片資料轉成單一 LINE Flex bubble"""
    title = f"{title_prefix}{card.get('名稱', '未知')}"
    return {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": title, "weight": "bold", "size": "xl", "align": "center", "wrap": True},
                {"type": "text", "text": card.get('英文名稱', 'Essential Oil'), "size": "sm", "align": "center", "color": "#888888"},
            ],
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "image", "url": card.get('image_url') or 'https://via.placeholder.com/300', "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{card.get('關鍵詞', '無')}", "margin": "md", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": card.get('心靈指引 (建議)', '無'), "wrap": True, "margin": "md", "size": "sm"},
            ],
        },
    }


def build_flex_carousel(cards_with_titles: list) -> dict:
    """把多張 (標題前綴, 卡片) tuple 組成 carousel，供三牌陣等模式使用"""
    bubbles = [build_flex_bubble(card, title_prefix=f"【{prefix}】") for prefix, card in cards_with_titles]
    return {"type": "carousel", "contents": bubbles}


# ==================================================================
# 5 組抽卡模式插槽（目前皆為隨機抽取 doterra.csv 假資料的樁程式）
# ==================================================================

def mode_1_daily_energy(user_id: str):
    """
    模式1：今日能量指引（單牌盲抽）
    24 小時內重複輸入「抽卡」一律回傳今天第一次抽到的卡，並附上提示文字。
    回傳：(flex_json, card_dict, note_or_None)
    """
    if is_locked_today(user_id):
        locked_card = get_locked_card(user_id)
        flex = build_flex_bubble(locked_card, title_prefix="【今日已鎖定】")
        note = "請勿重複抽卡影響標準值，這是你今天第一次抽到的卡。"
        return flex, locked_card, note

    oils_db = fetch_oils_data()
    if not oils_db:
        return None, None, "資料庫目前無可用資料。"

    drawn_card = random.choice(oils_db)
    lock_today_card(user_id, drawn_card)
    flex = build_flex_bubble(drawn_card, title_prefix="【今日能量指引】")
    return flex, drawn_card, None


def mode_2_three_cards(user_id: str):
    """
    模式2：身心靈三牌陣（一次盲抽 3 張不同的卡，分別對應身、心、靈）
    回傳：(flex_json, [card_dict, card_dict, card_dict], note_or_None)
    """
    oils_db = fetch_oils_data()
    if len(oils_db) < 3:
        return None, None, "資料庫牌數不足，無法進行三牌陣（目前為假資料樁）。"

    drawn_cards = random.sample(oils_db, 3)
    labels = ["身", "心", "靈"]
    cards_with_titles = list(zip(labels, drawn_cards))
    flex = build_flex_carousel(cards_with_titles)
    return flex, drawn_cards, None


def mode_3_issue_resolver(user_id: str, text: str):
    """
    模式3：特定困擾破局牌（單牌 + 預留 AI 大腦串接插槽）
    `text` 為使用者描述的困擾內容，目前僅原樣保留，尚未真正送進 AI。
    回傳：(flex_json, card_dict, note_or_None)
    """
    oils_db = fetch_oils_data()
    if not oils_db:
        return None, None, "資料庫目前無可用資料。"

    drawn_card = random.choice(oils_db)

    # TODO: 未來在此處串接 AI 大腦（例如呼叫 LLM API），
    # 將使用者困擾描述 `text` 與抽到的 `drawn_card` 一併送入模型，
    # 由模型生成客製化的破局建議文字，取代下方的假資料樁回覆。
    note = f"（AI 洞察插槽尚未串接，暫以卡牌預設指引取代：{drawn_card.get('心靈指引 (建議)', '無')}）"

    flex = build_flex_bubble(drawn_card, title_prefix="【破局指引】")
    return flex, drawn_card, note


CHAKRA_LIST = ["海底輪", "臍輪", "太陽神經叢輪", "心輪", "喉輪", "眉心輪", "頂輪"]


def mode_4_chakra_balance(user_id: str):
    """
    模式4：脈輪能量調和（盲抽對應脈輪的假卡）
    目前 CSV 尚未有脈輪欄位，先用隨機指派模擬對應關係；
    未來可在 doterra.csv 增加「脈輪」欄位取代此隨機邏輯。
    回傳：(flex_json, card_dict, note_or_None)
    """
    oils_db = fetch_oils_data()
    if not oils_db:
        return None, None, "資料庫目前無可用資料。"

    drawn_card = random.choice(oils_db)
    matched_chakra = random.choice(CHAKRA_LIST)
    flex = build_flex_bubble(drawn_card, title_prefix=f"【{matched_chakra}】")
    note = f"對應脈輪：{matched_chakra}"
    return flex, drawn_card, note


def mode_5_developer_debug():
    """
    模式5：開發者後門測試模式
    回傳 CSV 讀取狀況與記憶體鎖定狀態的純文字診斷報告，不產生 Flex Message。
    回傳：(None, None, report_text)
    """
    oils_db = fetch_oils_data()
    snapshot = debug_memory_snapshot()
    report = (
        "【開發者除錯報告】\n"
        f"CSV 資料筆數：{len(oils_db)}\n"
        f"今日已鎖定使用者數：{snapshot['locked_count']}\n"
        f"鎖定鍵值：{snapshot['keys']}"
    )
    return None, None, report
