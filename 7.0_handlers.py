import random
from database_manager import load_essential_oils

def get_oil_flex_message():
    oils_db = load_essential_oils()
    if not oils_db:
        return None, "系統維護中"
    
    drawn_oil = random.choice(oils_db)
    
    # 建立 Flex Message 結構，對應 doterra.csv 實際欄位
    flex_content = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "text", "text": drawn_oil.get('名稱', '未知'), "weight": "bold", "size": "xl", "align": "center"},
                {"type": "text", "text": drawn_oil.get('英文名稱', 'Essential Oil'), "size": "sm", "align": "center", "color": "#888888"}
            ]
        },
        "body": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "image", "url": drawn_oil.get('image_url') or 'https://via.placeholder.com/300', "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{drawn_oil.get('關鍵詞', '無')}", "margin": "md", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": drawn_oil.get('心靈指引 (建議)', '無'), "wrap": True, "margin": "md", "size": "sm"}
            ]
        }
    }
    return flex_content, drawn_oil.get('名稱')
