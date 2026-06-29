import random
from database_manager import load_essential_oils

def get_oil_flex_message():
    oils_db = load_essential_oils()
    if not oils_db:
        return None, None
    
    drawn_oil = random.choice(oils_db)
    
    # 建構符合 LINE 格式的 JSON
    flex_content = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "text", "text": drawn_oil['名稱'], "weight": "bold", "size": "xl", "align": "center"},
                {"type": "text", "text": drawn_oil['英文名稱'], "size": "sm", "align": "center", "color": "#888888"}
            ]
        },
        "body": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "image", "url": drawn_oil.get('image_url', 'https://via.placeholder.com/300'), "size": "full", "aspectMode": "cover"},
                {"type": "text", "text": f"關鍵詞：{drawn_oil['關鍵詞']}", "margin": "md", "wrap": True},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": drawn_oil['心靈指引 (建議)'], "wrap": True, "margin": "md", "size": "sm"}
            ]
        }
    }
    return flex_content, drawn_oil['名稱']
