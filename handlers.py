import random
from database_manager import fetch_oils_data

def get_drawing_response(user_id):
    """
    從資料庫隨機抽取精油，並回傳 flex_json 與資料字典
    """
    oils_db = fetch_oils_data()
    if not oils_db:
        return None, None
    
    drawn_oil = random.choice(oils_db)
    
    # 建構符合 LINE Flex Message 規範的 JSON 結構
    flex_content = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": drawn_oil.get('名稱', '未知'), "weight": "bold", "size": "xl", "align": "center"},
                {"type": "text", "text": drawn_oil.get('英文名稱', 'Essential Oil'), "size": "sm", "align": "center", "color": "#888888"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "image", "url": drawn_oil.get('image_url') or 'https://via.placeholder.com/300', "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{drawn_oil.get('關鍵詞', '無')}", "margin": "md", "weight": "regular", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": drawn_oil.get('心靈指引 (建議)', '無'), "wrap": True, "margin": "md", "size": "sm"}
            ]
        }
    }
    return flex_content, drawn_oil
