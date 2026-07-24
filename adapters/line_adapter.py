def _build_bubble(card: dict, label: str = None) -> dict:
    header_contents = []
    if label:
        header_contents.append({"type": "text", "text": label,
                                 "size": "xs", "color": "#B08968", "align": "center"})
    header_contents += [
        {"type": "text", "text": card.get("name", "未知"),
         "weight": "bold", "size": "xl", "align": "center"},
        {"type": "text", "text": card.get("name_en", ""),
         "size": "sm", "align": "center", "color": "#888888"},
    ]

    body_contents = [
        {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": "關鍵詞", "size": "xs", "color": "#B08968", "flex": 1},
                {"type": "text", "text": card.get("keywords", "無"), "size": "sm",
                 "color": "#555555", "flex": 4, "wrap": True},
            ],
        },
    ]

    # 脈輪欄位只有在實際有內容時才顯示，複方精油卡本身無此欄位，不強行塞入空白列
    chakra = (card.get("chakra") or "").strip()
    if chakra:
        body_contents.insert(0, {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": "脈輪", "size": "xs", "color": "#B08968", "flex": 1},
                {"type": "text", "text": chakra, "size": "sm",
                 "color": "#555555", "flex": 4, "wrap": True},
            ],
        })

    body_contents.append({"type": "separator", "margin": "md"})

    # 描述欄位同樣只有內容存在時才顯示；guidance 心靈小語每張卡都一定有，維持必顯示
    description = (card.get("description") or "").strip()
    guidance_text = card.get("guidance", "無")
    if description:
        body_contents.append({
            "type": "text", "text": guidance_text,
            "wrap": True, "margin": "md", "size": "sm", "color": "#333333",
        })
        body_contents.append({"type": "separator", "margin": "md"})
        body_contents.append({
            "type": "text", "text": description,
            "wrap": True, "margin": "md", "size": "xs", "color": "#777777",
        })
    else:
        body_contents.append({
            "type": "text", "text": guidance_text,
            "wrap": True, "margin": "md", "size": "sm", "color": "#333333",
        })

    return {
        "type": "bubble",
        "header": {"type": "box", "layout": "vertical", "contents": header_contents},
        "hero": {
            "type": "image",
            "url": card.get("image_url"),
            "size": "full",
            "aspectRatio": "4:3",
            "aspectMode": "cover",
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": body_contents,
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "看完整解析",
                        "uri": f"{BASE_URL}/oil/{card.get('id', '')}",
                    },
                },
                {
                    "type": "button",
                    "style": "primary",
                    "height": "sm",
                    "color": "#B08968",
                    "action": {
                        "type": "uri",
                        "label": "前往專屬商城",
                        "uri": SHOP_URL,
                    },
                },
            ],
        },
    }
