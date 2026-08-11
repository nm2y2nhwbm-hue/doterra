"""
抽卡紀錄模組：獨立於精油資料庫，只負責記錄「誰、何時、抽了什麼」。
以 CSV 追加寫入，注意 Render 免費方案重新部署時檔案系統會重置，
這是輕量級紀錄，非長期資料庫，如需長期保存建議之後接外部試算表或資料庫。
"""
from core import database_manager as db


def log_draw(user_id: str, display_name: str, mode: str, card_names: list):
    try:
        return db.save_draw({
            'user_id': user_id, 'display_name': display_name,
            'mode': mode, 'cards': card_names,
        })
    except Exception as e:
        print(f"[draw_logger] 寫入紀錄失敗: {e}")
        return False
