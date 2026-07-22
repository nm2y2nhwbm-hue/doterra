"""
商業抽卡演算法核心（現代精油心靈指引卡 5 大牌陣版）。
與通訊外殼完全解耦：只吃 user_id / 文字參數，只吐 ActionResult dict。
"""
import random

from core import database_manager as db
from core import memory_manager as mem

INDICATOR_SYMBOLS = [
    "魚", "愛心", "戒指", "孩童", "狗", "月亮",
    "樹", "十字路口", "船", "鸛鳥", "房屋", "熊",
]


def _draw_unique(n: int):
    pool = db.fetch_oils_data()
    if len(pool) < n:
        return None
    return random.sample(pool, n)


def mode_1_today_energy(user_id: str) -> dict:
    """模式1：今日能量指引（單牌），24 小時內鎖定同一張卡。"""
    if mem.is_locked_today(user_id):
        return {"type": "flex_single", "mode": "mode_1",
                "card": mem.get_locked_card(user_id), "locked": True}

    cards = _draw_unique(1)
    if not cards:
        return {"type": "text", "text": "目前卡牌資料庫為空，請聯絡管理員。"}

    card = cards[0]
    mem.lock_today_card(user_id, card)
    return {"type": "flex_single", "mode": "mode_1", "card": card, "locked": False}


def mode_2_life_guidance(user_id: str) -> dict:
    """模式2：生活導引牌陣（兩張不重複）。"""
    cards = _draw_unique(2)
    if not cards:
        return {"type": "text", "text": "卡牌數量不足，無法進行生活導引牌陣。"}

    positions = [
        {"label": "目前整體狀況", "card": cards[0]},
        {"label": "生活中所需的建議及方向", "card": cards[1]},
    ]
    return {"type": "flex_positions", "mode": "mode_2", "positions": positions}


def mode_3_body_mind_spirit(user_id: str) -> dict:
    """模式3：療癒身心靈牌陣（三張不重複，嚴格排序）。"""
    cards = _draw_unique(3)
    if not cards:
        return {"type": "text", "text": "卡牌數量不足，無法進行療癒身心靈牌陣。"}

    positions = [
        {"label": "身體狀況及提升精油", "card": cards[0]},
        {"label": "心理狀況及提升精油", "card": cards[1]},
        {"label": "精神狀況及提升精油", "card": cards[2]},
    ]
    return {"type": "flex_positions", "mode": "mode_3", "positions": positions}


def mode_4_self_awareness(user_id: str) -> dict:
    """模式4：暸解自我牌陣（三張不重複，嚴格排序）。"""
    cards = _draw_unique(3)
    if not cards:
        return {"type": "text", "text": "卡牌數量不足，無法進行暸解自我牌陣。"}

    positions = [
        {"label": "別人眼中的你", "card": cards[0]},
        {"label": "私底下獨處時的你", "card": cards[1]},
        {"label": "真正的你", "card": cards[2]},
    ]
    return {"type": "flex_positions", "mode": "mode_4", "positions": positions}


def mode_5_indicator_spread(user_id: str, indicator_symbol: str) -> dict:
    """模式5：單一指示牌陣。指示牌決定主題，左右各抽 1 張不重複精油卡。"""
    if indicator_symbol not in INDICATOR_SYMBOLS:
        return {"type": "text", "text": "請指定有效的指示象徵：魚、愛心、戒指、孩童、狗、月亮、樹、十字路口、船、鸛鳥、房屋、熊。"}

    cards = _draw_unique(2)
    if not cards:
        return {"type": "text", "text": "卡牌數量不足，無法進行單一指示牌陣。"}

    positions = [
        {"label": f"「{indicator_symbol}」左側提升精油", "card": cards[0]},
        {"label": f"「{indicator_symbol}」右側提升精油", "card": cards[1]},
    ]
    return {"type": "flex_positions", "mode": "mode_5",
            "indicator": indicator_symbol, "positions": positions}
