"""
商業抽卡演算法核心。
刻意設計成「輸入純資料、輸出純資料（ActionResult dict）」，
完全不 import linebot、不認識 Flex Message —— 這樣未來加 Discord Bot
或一頁式網頁時，這個檔案可以一行都不用改。
"""
import random

from core import database_manager as db
from core import memory_manager as mem


def _draw_random(pool=None):
    oils = pool if pool is not None else db.fetch_oils_data()
    if not oils:
        return None
    return random.choice(oils)


def mode_1_today_energy(user_id: str) -> dict:
    """mode_1：今日能量，24 小時內鎖定同一張卡。"""
    if mem.is_locked_today(user_id):
        card = mem.get_locked_card(user_id)
        return {"type": "flex_card", "mode": "mode_1", "card": card, "locked": True}

    card = _draw_random()
    if not card:
        return {"type": "text", "text": "目前卡牌資料庫為空，請聯絡管理員。"}

    mem.lock_today_card(user_id, card)
    return {"type": "flex_card", "mode": "mode_1", "card": card, "locked": False}


def mode_2_three_card_spread(user_id: str) -> dict:
    """mode_2：三牌陣，不重複抽取 3 張卡。"""
    pool = db.fetch_oils_data()
    if len(pool) < 3:
        return {"type": "text", "text": "卡牌數量不足，無法進行三牌陣抽選。"}

    cards = random.sample(pool, 3)
    return {"type": "flex_carousel", "mode": "mode_2", "cards": cards}


def mode_3_breakthrough(user_id: str, user_question: str = "") -> dict:
    """
    mode_3：困擾破局。
    TODO：串接 OpenAI gpt-4o-mini，依 user_question 語意分析後挑選對應精油卡牌。
    """
    # TODO(OpenAI gpt-4o-mini 整合):
    # from openai import OpenAI
    # client = OpenAI()
    # resp = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "你是一位精油心靈指引師，"
    #                                        "請根據使用者的困擾，從候選精油關鍵詞中挑出最貼切的一張。"},
    #         {"role": "user", "content": user_question},
    #     ],
    # )
    # 依 resp 內容比對 db.fetch_oils_data() 選出對應卡牌...

    # 目前先以隨機抽卡作為 fallback，待 AI 邏輯完成後取代
    card = _draw_random()
    if not card:
        return {"type": "text", "text": "目前卡牌資料庫為空，請聯絡管理員。"}
    return {"type": "flex_card", "mode": "mode_3", "card": card, "ai_powered": False}


def mode_4_chakra_pick(user_id: str, chakra: str) -> dict:
    """mode_4：脈輪分類抽選。"""
    pool = db.get_oils_by_chakra(chakra)
    if not pool:
        return {"type": "text", "text": f"目前找不到「{chakra}」對應的精油卡牌。"}

    card = _draw_random(pool)
    return {"type": "flex_card", "mode": "mode_4", "card": card, "chakra": chakra}


def mode_5_debug_report(user_id: str) -> dict:
    """mode_5：系統 debug 報告。"""
    oils = db.fetch_oils_data()
    lines = [
        "【系統 Debug 報告】",
        f"卡牌總數：{len(oils)}",
        f"目前鎖定中的使用者數：{len(mem.USER_ENERGY_MEMORY)}",
        f"可用脈輪分類：{', '.join(db.get_all_chakras()) or '無'}",
    ]
    return {"type": "text", "text": "\n".join(lines)}