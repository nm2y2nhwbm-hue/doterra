# 現代精油心靈指引卡 · 雫之洞悉 · 返魂堂
> **MODERN OIL ORACLE** —— 結合多特瑞純粹植物精油與日系塔羅直覺的 3 分鐘身心校準與自然醫學調息全書平台。

[![Vercel Deployment](https://img.shields.io/badge/Vercel-READY-355343?logo=vercel&logoColor=white)](https://doterra-two.vercel.app/)
[![Render Backend](https://img.shields.io/badge/Render-Online-22c55e?logo=render&logoColor=white)](https://doterra-73pv.onrender.com/health)
[![Supabase Database](https://img.shields.io/badge/Supabase-Healthy-3ecf8e?logo=supabase&logoColor=white)](https://supabase.com/)
[![PageSpeed Desktop](https://img.shields.io/badge/PageSpeed-95%2F100-brightgreen?logo=googlechrome&logoColor=white)](https://pagespeed.web.dev/analysis/https-doterra-two-vercel-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 1. 專案名稱與一句話介紹

**雫之洞悉 · 返魂堂（MODERN OIL ORACLE）** 是一套以日式款待美學（おもてなし）為核心打造的現代精油心靈互動系統。為繁忙的高壓現代人提供 3 分鐘身心自我校準儀式，無縫串聯 **LINE 官方帳號**、**LIFF 全螢幕抽卡**、**131 款自然醫學精油圖鑑**、**線上預約接待後台** 與 **雲端庫存儀表板**。

* **正式線上展示站**：[https://doterra-two.vercel.app/](https://doterra-two.vercel.app/)
* **LINE 官方應用入口**：[https://miniapp.line.me/2010916161-HrIOEAda](https://miniapp.line.me/2010916161-HrIOEAda)
* **後端 API 伺服器**：[https://doterra-73pv.onrender.com/](https://doterra-73pv.onrender.com/)

---

## ✨ 2. 功能特色列表

* 🔮 **12 大主題牌陣線上抽卡**
  * **🪞 鏡子（模式 1~5）**：照看當下·今日能量、生活導引、三牌陣（身心靈深度解析）、探索自我與單一指示牌。
  * **🌊 河流（模式 6~10）**：時間流動·月運勢、二選一決策與年度生命軌跡梳理。
  * **⛩️ 岔路（模式 11~12）**：十字路口·重大人生決策與深度心靈香氣解方。
* 🌿 **131 款「精油圖鑑 · 自然醫學調息全書」**
  * 完整收錄 131 款純粹單方與複方精油，依「臣、使、佐」三大身心位格、性味歸經與調息處方箋速查。
  * 嚴格落實法規合規，以「自然醫學調息」取代宣稱療效的醫療診斷語彙。
* 📲 **LINE 官方帳號與 LIFF 原生無縫整合**
  * 圖文選單點選文字即時辨識，後台回傳帶直跳按鈕之 Flex Message 卡片。
  * 支援短效 Opaque Handoff 憑證，防止體驗碼於 URL 或前台被篡改偽造。
* 💎 **貴賓一對一調息禮盒預約系統**
  * 整合線上預約表單，自動生成專屬流水受付編號（如 REC-20260901-0001）。
  * 伺服器端嚴格校驗防重複提交、防惡意連點，保障名單安全。
* 🛡️ **頂級資安防禦與權限架構**
  * **Stored XSS 防禦**：管理後台對預約人姓名、Email、LINE ID、備註等輸入欄位全面採用純文字實體編碼跳脫。
  * **Edge Function 白名單驗證**：庫存同步函式嚴格校驗管理員 JWT 與資料表白名單，防止非授權竄改。
* 📊 **行動友善日式管理後台**
  * **受付處（eception.html）**：預約清單、受付編號檢索、抽牌明細展開與處理狀態管理。
  * **庫存儀表板（inventory.html）**：瓶數即時統計、60 天效期預警、相機掃描條碼與 Google 試算表雙向同步。
  * **站點監控中心（sites.html）**：GitHub、Render、Vercel、Supabase 與 LINE Webhook 全站健康探測。
* ⚡ **PageSpeed 95+ 極速效能體驗**
  * 日系旗艦字型（LINESeedTW）零阻斷非同步載入架構。
  * 高解析圖片 85% 深度壓縮、尺寸嚴格標註，達成 0.000 累積版面位移（CLS）。

---

## 🛠️ 3. 技術架構

| 層級 | 使用技術 | 說明 |
| :--- | :--- | :--- |
| **前端 (Frontend)** | HTML5, Vanilla JavaScript (ES6+), CSS3 | 日式和紙侘寂風客製化樣式、CSS Variables、非同步字型載入、無第三方肥大框架負擔 |
| **後端 (Backend)** | Python 3.8+, Flask, LineBotSDK, Gunicorn | 處理 LINE Webhook、事件路由、安全 Hand-off 抽卡交接與公開唯讀資料 API |
| **邊緣運算 (Edge)** | Deno, Supabase Edge Functions | sync-inventory 實現 Google 試算表自動彙總與庫存同步 |
| **資料庫 (Database)** | Supabase (PostgreSQL 15+) | RLS（Row Level Security）、SECURITY DEFINER 安全 RPC 函式、Check Constraints 約束 |
| **部署託管 (Cloud)** | Vercel, Render | Vercel 託管靜態前端與邊緣快取；Render 託管 Python 後端 Web 服務 |
| **整合協定 (Protocols)** | LINE Messaging API, LIFF (LINE Front-end Framework), GA4 | LINE 雙向通訊、全螢幕抽卡容器、Google Analytics 4 流量數據分析 |

---

## 🚀 4. 安裝與本地啟動

### 步驟 1：複製專案
`ash
git clone https://github.com/nm2y2nhwbm-hue/doterra.git
cd doterra
`

### 步驟 2：安裝後端依賴套件
建議使用虛擬環境（env 或 conda）：
`ash
python -m venv venv
# Windows 啟動虛擬環境:
venv\Scripts\activate
# macOS / Linux 啟動虛擬環境:
source venv/bin/activate

pip install -r requirements.txt
`

### 步驟 3：設定環境變數
在專案根目錄建立 .env 檔案（請勿將包含金鑰的檔案提交至 Git）：
`env
CHANNEL_ACCESS_TOKEN="你的_LINE_CHANNEL_ACCESS_TOKEN"
CHANNEL_SECRET="你的_LINE_CHANNEL_SECRET"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"
`

### 步驟 4：啟動本機伺服器
* **啟動 Python 後端 Webhook 服務**：
  `ash
  python line_bot.py
  # 伺服器將於 http://localhost:5000 啟動，探測路徑：http://localhost:5000/health
  `
* **啟動前端靜態預覽**：
  `ash
  # 使用 Python 內建伺服器預覽 static 目錄
  python -m http.server 8000 -d static
  # 瀏覽器造訪：http://localhost:8000/
  `

---

## 📁 5. 資料夾結構說明

`	ext
doterra/
├── adapters/                  # 介面轉接層
│   └── line_adapter.py        # 將核心邏輯結果轉換為 LINE Flex Message 卡片
├── core/                      # 系統核心商業邏輯
│   ├── card_deck.py           # 69 張精油卡與 12 張指示卡資料庫核心
│   ├── database_manager.py    # 資料讀取與 CSV 聚合處理
│   ├── draw_logger.py         # 抽卡歷史紀錄與統計
│   └── experience_handoff.py  # 安全抽卡交接 Token 與防偽機制
├── static/                    # 前端靜態網站根目錄（Vercel 部署目標）
│   ├── index.html             # 官網首頁（Hero 區、3 欄牌陣介紹、安心承諾、預約表單）
│   ├── cards.html             # 線上抽卡主工具頁面（支援 12 種模式與 LIFF 容器）
│   ├── oils.html              # 精油圖鑑 · 自然醫學調息全書（131 款精油與搜尋篩選）
│   ├── booking.html           # 貴賓調息禮盒一對一正式預約表單
│   ├── admin.html             # 後台管理入口首頁（4 大模組導航與登入守門）
│   ├── reception.html         # 受付與抽牌紀錄（預約名單、狀態更新、明細展開）
│   ├── inventory.html         # 精油庫存管理（條碼掃描、Google 試算表同步）
│   ├── sites.html             # 站點健康監測中心（Render, Vercel, LINE Webhook 探測）
│   ├── style.css              # 日式極簡美學核心樣式表
│   ├── fonts.css              # LINESeedTW 字型非同步載入樣式
│   ├── script.js              # 抽卡流程、動畫與體驗碼主控制器
│   ├── supabase-client.js     # 前端 Supabase Client 初始化與 RPC 包裝
│   ├── images/                # 品牌 Logo、水墨紋樣與卡牌圖檔
│   └── fonts/                 # LINESeedTW 繁體中文 WebFont 檔案
├── supabase/                  # 資料庫遷移腳本與 Edge Functions
│   ├── supabase_schema.sql    # 完整資料表結構、RLS 策略與 RPC 函式定義
│   ├── migrations/            # 版本化資料庫遷移紀錄（依時間戳命名）
│   └── functions/             # Supabase Edge Functions (sync-inventory)
├── AGENTS.md                  # AI 協同開發與品質稽核規範指引
├── doterra.csv                # 131 款現代精油核心資料庫（性味歸經、位格、調息箋）
├── indicator_cards.csv        # 12 款指示卡元資料
├── line_bot.py                # 後端 Flask Webhook 主程式入口
├── router.py                  # LINE 訊息文字意圖解析與分發路由
├── requirements.txt           # Python 套件清單
└── vercel.json                # Vercel 安全標頭與路由配置
`

---

## ❓ 6. 常見問題 (FAQ)

### Q1：為什麼在 LINE 點擊圖文選單時，能瞬間跳轉對應牌陣？
> 本系統採用「雙重偵測與即時直跳路由」機制：  
> 1. 用戶點擊選單發送關鍵字（如 【🪞 鏡子 1~5】）時，outer.py 即時回傳帶有專屬 Category 參數的 LIFF 連結。  
> 2. 首頁 <head> 第一行內建 User-Agent 偵測，若在 LINE App 內直接點開網址，會在 0.05 秒內無感重新導向至卡牌頁面，跳過行銷首頁直接開抽。

### Q2：抽牌後的「體驗碼」如何防止偽造或外流？
> 系統廢棄了早期的 URL 參數傳遞體驗碼（experience_code），全面改採 **短效 Opaque Handoff 機制**：  
> 抽卡完成後只在伺服器端產生一組加密雜湊的短效憑證（有效期限 600 秒），使用者必須透過 LINE 登入／LIFF 驗證其真實身分後，才能解鎖並兌換真正的體驗碼。

### Q3：後台點擊「全部歸零」出現 DELETE requires a WHERE clause 該如何解決？
> 這是因為 Supabase / PostgreSQL 啟用了 safeupdate 安全擴充套件，強制所有 DELETE 語句必須包含條件式。  
> 請確認已套用最新遷移腳本 20260828131800_fix_admin_reset_reception_where_clause.sql，該版本已在 RPC 函式內加入 WHERE true 並宣告 SECURITY DEFINER，即可安全執行全表歸零。

### Q4：網站文案與圖鑑內容是否有合規風險？
> 全站文案與 131 款精油處方箋，皆已嚴格依據台灣相關法規進行合規校正：全面去除「治療、抗炎、療效、處方」等具醫療診斷暗示之用語，統一代換為 **「自然醫學調息箋」、「身心校準」、「撫慰調適」**，兼顧專業深度與法律合規。

---

## 🤝 7. 貢獻與授權條款 (Contributing & License)

### 如何參與貢獻
1. **Fork 本專案** 至個人 GitHub 帳號。
2. 建立功能分支（git checkout -b feature/amazing-feature）。
3. 遵循 AGENTS.md 規範進行開發，並執行語法與安全性檢查。
4. 提交 Commit（git commit -m 'feat: 新增特定牌陣支援'）。
5. 推送至分支（git push origin feature/amazing-feature）並發起 **Pull Request**。

### 授權條款 (License)
本專案採 **MIT License** 授權開源，詳細條款請參閱根目錄之 [LICENSE](LICENSE) 檔案。  
*精油資料庫與「雫之洞悉 · 返魂堂」品牌識別著作權保留予原作者所有。*