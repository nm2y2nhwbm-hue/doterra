import random
from database_manager import fetch_oils_data

def get_drawing_response():
    oils_db = fetch_oils_data()
    if not oils_db:
        return "🔮 系統維護中..."
    
    oil = random.choice(oils_db)
    return (
        f"🔮【返魂堂·精油洞悉卡今日指引】🔮\n\n"
        f"🌿 今日有緣精油：{oil.get('產品名稱')}\n"
        f"📐 能量位格歸屬：{oil.get('位格歸屬')}\n\n"
        f"🧘‍♂️ 心靈指引：\n{oil.get('名醫建議 (專家理論基礎 + 核心效益組合)')}\n\n"
        f"====================\n"
        f"🛠️【日常使用與防護指南】\n"
        f"• 使用方式：{oil.get('用法標籤')}\n"
        f"• 塗抹建議：{oil.get('塗抹建議')}"
    )