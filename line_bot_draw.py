# 建議優化後的 line_bot_draw.py 中的 handle_message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id 
    user_text = event.message.text
    
    try:
        if any(k in user_text for k in ["抽牌", "抽卡", "draw"]):
            reply, _ = get_drawing_response(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            
        elif any(k in user_text for k in ["解釋", "更多", "說明"]):
            reply = get_followup_response(user_id)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
            
    except Exception as e:
        # 當伺服器發生任何意外錯誤時，傳送給 LINE 用戶一個提示
        print(f"Error: {e}") # 這會在 Render Logs 顯示，方便你偵錯
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="🔮 系統暫時迷路了，請再試一次或輸入「抽牌」重新開始。")
        )