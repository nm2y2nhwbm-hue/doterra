"""
抽卡紀錄模組：獨立於精油資料庫，只負責記錄「誰、何時、抽了什麼」。
以 CSV 追加寫入，注意 Render 免費方案重新部署時檔案系統會重置，
這是輕量級紀錄，非長期資料庫，如需長期保存建議之後接外部試算表或資料庫。
"""
import csv
from datetime import datetime, timezone
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parent.parent
_LOG_CSV = _PROJECT_ROOT / 'draw_logs.csv'

_HEADERS = ['timestamp', 'user_id', 'display_name', 'mode', 'cards']


def _ensure_header():
    if not _LOG_CSV.is_file():
        with open(_LOG_CSV, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(_HEADERS)


def log_draw(user_id: str, display_name: str, mode: str, card_names: list):
    try:
        _ensure_header()
        if isinstance(card_names, (list, tuple)):
            clean_cards = '、'.join(str(c).strip() for c in card_names if c)
        else:
            clean_cards = str(card_names or '').strip()

        with open(_LOG_CSV, mode='a', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now(timezone.utc).isoformat(),
                str(user_id or '')[:64],
                str(display_name or '')[:64],
                str(mode or '')[:32],
                clean_cards[:500],
            ])
        return True
    except Exception as e:
        print(f"[draw_logger] 寫入紀錄失敗: {e}")
        return False
