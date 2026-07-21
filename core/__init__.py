import csv
import os
from datetime import datetime

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'doterra.csv')

# ------------------------------------------------------------------
# 記憶體鎖定字典
# 用途：鎖定「當天日期 + user_id」，避免使用者 24 小時內重複抽卡。
# 格式：{ "YYYY-MM-DD_userId": {卡片資料 dict} }
# 注意：這是純記憶體結構，重啟服務（例如 Render 重新部署）後會清空，
#      未來若需要跨重啟保存，可替換成 Redis 或資料庫。
# ------------------------------------------------------------------
USER_ENERGY_MEMORY = {}


def fetch_oils_data():
    """
    讀取 doterra.csv，回傳精油卡片資料的 list[dict]。
    自動嘗試多種常見編碼，直到成功為止。
    """
    encodings = ['utf-8-sig', 'utf-8', 'big5', 'cp950']

    for enc in encodings:
        try:
            with open(CSV_FILE, mode='r', encoding=enc) as f:
                reader = csv.reader(f)
                next(reader)  # 略過標題列

                oils_list = []
                for row in reader:
                    if row and row[0].strip():
                        oils_list.append({
                            "名稱": row[0].strip(),
                            "英文名稱": row[1].strip() if len(row) > 1 else "",
                            "關鍵詞": row[2].strip() if len(row) > 2 else "",
                            "心靈指引 (建議)": row[3].strip() if len(row) > 3 else "",
                            "image_url": row[4].strip() if len(row) > 4 else "",
                        })

                if oils_list:
                    print(f"[database_manager] 使用編碼 {enc} 成功讀取到 {len(oils_list)} 筆資料")
                    return oils_list
        except Exception:
            continue  # 這個編碼失敗，換下一個試試看

    print("[database_manager] 錯誤：無法以任何編碼讀取 CSV")
    return []


def _today_key(user_id: str) -> str:
    """組出「當天日期_user_id」的鎖定鍵值"""
    today_str = datetime.now().strftime('%Y-%m-%d')
    return f"{today_str}_{user_id}"


def get_locked_card(user_id: str):
    """查詢使用者今天是否已經抽過卡，若有則回傳當時抽到的卡片 dict，否則回傳 None"""
    return USER_ENERGY_MEMORY.get(_today_key(user_id))


def lock_today_card(user_id: str, card: dict) -> None:
    """將使用者今天第一次抽到的卡鎖進記憶體，之後同一天都回傳這張"""
    USER_ENERGY_MEMORY[_today_key(user_id)] = card


def is_locked_today(user_id: str) -> bool:
    """使用者今天是否已經被鎖定過一張卡"""
    return _today_key(user_id) in USER_ENERGY_MEMORY


def debug_memory_snapshot() -> dict:
    """提供 mode_5 開發者後門使用，回傳目前記憶體鎖定狀態的快照"""
    return {
        "locked_count": len(USER_ENERGY_MEMORY),
        "keys": list(USER_ENERGY_MEMORY.keys()),
    }
