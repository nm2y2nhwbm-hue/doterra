"""
獨立工具模組：字串清洗工具
與商業邏輯、通訊外殼完全無關，可被任何模組單獨引用測試。
"""
import re


def slugify_name_en(name_en: str) -> str:
    """
    將精油英文名稱轉為適合當檔名的 slug。
    規則：
      1. 轉為純小寫
      2. 所有「非英數字元」（空格、逗號、® 等）一律替換為連字號 "-"
      3. 去除前後贅字（多餘的連字號）

    範例：
        "Sandalwood, Hawaiian"  -> "sandalwood-hawaiian"
        "Fennel-Sweet"          -> "fennel-sweet"
        "Ylang Ylang®"          -> "ylang-ylang"
    """
    if not name_en:
        return ""

    text = name_en.strip().lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text
