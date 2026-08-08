"""
商業抽卡演算法核心（V2：純導流版）。
5 大牌陣的實際抽卡邏輯已搬遷至前端 static/cards.html 執行，
本檔案只保留「指示牌象徵清單」查詢，供 router.py 使用。
"""
from core import database_manager as db


def _get_indicator_symbols():
    """從 indicator_cards.csv 動態讀取指示象徵清單，不寫死於程式碼中。"""
    return db.get_indicator_names()
