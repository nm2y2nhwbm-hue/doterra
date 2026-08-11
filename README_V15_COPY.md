# 洞悉卡 V15 移植備用副本

這是由 GitHub 正式版結構衍生的獨立備用副本，不會覆蓋原專案。

## 已移植功能

- V15 一頁式 Landing Page、雙 CTA 與預約表單
- 五種抽牌模式
- 模式 5：選指示牌 → 正／反位 → 插入完整牌組 → 洗牌 → 揭示左右精油
- SQLite 持久化受付與抽牌紀錄
- 權杖保護的管理頁（`/?admin=1`）
- LINE LIFF 結果回傳與 Mobile-first 操作

## 本機啟動

1. 建立 Python 虛擬環境並安裝 `requirements.txt`。
2. 將 `.env.example` 複製為 `.env`，填入 LINE 與管理權杖設定。
3. 執行 `python line_bot.py`。
4. 開啟 `http://localhost:5000/`。

## 管理後台

開啟 `http://localhost:5000/?admin=1`，輸入 `.env` 的 `ADMIN_TOKEN`。

SQLite 預設檔案為 `doterra.sqlite3`；正式部署時請將 `DATABASE_PATH` 指向具持久磁碟的路徑。

上線前請重新核對禮盒品項、品牌／認證授權文字、LINE 憑證與 CORS 網域。任何見證皆須取得同意並保留可核對來源。
