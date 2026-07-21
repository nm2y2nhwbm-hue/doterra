"""
獨立記憶模組：管理「今日能量」24 小時鎖定狀態。
不依賴 Flask/LINE，未來 Discord Bot 可直接共用同一份記憶。
"""
from datetime import date

# Key 格式：f"{today_str}_{user_id}"
USER_ENERGY_MEMORY = {}


def _make_key(user_id: str) -> str:
    today_str = date.today().isoformat()
    return f"{today_str}_{user_id}"


def is_locked_today(user_id: str) -> bool:
    """無狀態防呆：判斷該使用者今天是否已抽過並鎖定。"""
    return _make_key(user_id) in USER_ENERGY_MEMORY


def get_locked_card(user_id: str):
    """取得今日已鎖定的卡牌，若無則回傳 None。"""
    return USER_ENERGY_MEMORY.get(_make_key(user_id))


def lock_today_card(user_id: str, card: dict) -> None:
    """將指定卡牌鎖定為該使用者今日結果。"""
    USER_ENERGY_MEMORY[_make_key(user_id)] = card


def clear_today_lock(user_id: str) -> None:
    """
    安全清除今日鎖定（白名單解鎖用）。
    使用 pop(key, None)，即使 key 不存在也不會 KeyError。
    """
    USER_ENERGY_MEMORY.pop(_make_key(user_id), None)


def clear_all_locks() -> None:
    """系統管理用：一次清空所有使用者鎖定（debug / 重置用）。"""
    USER_ENERGY_MEMORY.clear()