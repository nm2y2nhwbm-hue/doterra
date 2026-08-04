"""
商業抽卡演算法核心（V2：純導流版）。
5 大牌陣的實際抽卡邏輯已搬遷至前端 static/cards.html 執行，
本檔案只保留「指示牌象徵清單」查詢與文字提示，供 LINE 端 router.py 使用。
"""
from core import database_manager as db


def _get_indicator_symbols():
    """從 indicator_cards.csv 動態讀取指示象徵清單，不寫死於程式碼中。"""
    return db.get_indicator_names()


def mode_5_prompt_for_indicator() -> dict:
    """
    使用者透過純文字提及模式 5 但尚未指定象徵符號時的提示。
    正式的指示牌選擇與洗牌流程，已在 static/cards.html 前端完成。
    """
    symbols = "、".join(_get_indicator_symbols())
    return {
        "type": "text",
        "text": f"請於牌陣頁面中選擇指示象徵，例如：{symbols}",
        "mode": "mode_5_prompt",
    }
