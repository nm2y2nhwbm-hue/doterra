# 現代精油心靈指引卡 · 雫之洞悉 · 返魂堂
> **MODERN OIL ORACLE** —— 結合多特瑞純粹植物精油與日系塔羅直覺的 3 分鐘身心校準、自然醫學調息全書與五星 Agent 專業分工電商平台。

[![Vercel Deployment](https://img.shields.io/badge/Vercel-READY-355343?logo=vercel&logoColor=white)](https://doterra-two.vercel.app/)
[![Render Backend](https://img.shields.io/badge/Render-Online-22c55e?logo=render&logoColor=white)](https://doterra-73pv.onrender.com/health)
[![Supabase Database](https://img.shields.io/badge/Supabase-Healthy-3ecf8e?logo=supabase&logoColor=white)](https://supabase.com/)
[![GitHub Actions CI](https://img.shields.io/badge/CI-Passing-brightgreen?logo=githubactions&logoColor=white)](https://github.com/nm2y2nhwbm-hue/doterra/actions)
[![Agent Architecture](https://img.shields.io/badge/Architecture-5--Agent%20System-blueviolet)](AGENTS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 1. 專案名稱與一句話介紹

**雫之洞悉 · 返魂堂（MODERN OIL ORACLE）** 是一套以日式款待美學（おもてなし）為核心打造的現代精油心靈互動系統。為繁忙的高壓現代人提供 3 分鐘身心自我校準儀式，無縫串聯 **LINE 官方帳號**、**LIFF 全螢幕抽卡**、**131 款自然醫學精油圖鑑**、**全站日式側滑購物車**、**線上預約接待後台**、**雲端庫存儀表板** 與 **五大 Agent 專業分工體系**。

* **正式線上展示站**：[https://doterra-two.vercel.app/](https://doterra-two.vercel.app/)
* **LINE 官方應用入口**：[https://miniapp.line.me/2010916161-HrIOEAda](https://miniapp.line.me/2010916161-HrIOEAda)
* **後端 API 伺服器**：[https://doterra-73pv.onrender.com/](https://doterra-73pv.onrender.com/)

---

## ✨ 2. 功能特色列表

* 🔮 **12 大主題牌陣線上抽卡**
  * **🪞 鏡子（模式 1~5）**：照看當下·今日能量、生活導引、三牌陣（身心靈深度解析）、探索自我與單一指示牌。
  * **🌊 河流（模式 6~10）**：時間流動·月運勢、二選一決策與年度生命軌跡梳理。
  * **⛩️ 岔路（模式 11~12）**：十字路口·重大人生決策與深度心靈香氣解方。
* 🛒 **全站日式側滑購物車 (Cart Drawer) 與選品商城**
  * 日式極簡側滑抽屜體驗，支援數量增減、購物袋清空、商品移除與即時建議零售價總計。
  * 採用 `localStorage` 本地狀態持久化管理，關閉網頁或跨頁切換不遺失選品。
  * 一鍵將所選精油與禮盒資訊帶入貴賓預約表單進行結帳諮詢。
* 🏷️ **多特瑞官方單一「建議零售價」與容量規格透明機制**
  * 徹底去除雙軌定價疑惑，全站 131 款精油與 4 大禮盒全面採用台灣多特瑞官方單一「建議零售價」。
  * 規格嚴格落實多特瑞官方標準（15ml / 5ml / 10ml 滾珠 / 115ml 基底油）。
  * 首頁 4 大禮盒（鏡子組 NT$1,845、河流組 NT$1,965、岔路組 NT$4,895、客製滾珠油 NT$1,040）容量與價值精準對等。
* 🌿 **131 款「精油圖鑑 · 自然醫學調息全書」**
  * 完整收錄 131 款純粹單方與複方精油，依「中柱、右柱、左柱」三大身心位格、性味歸經與調息處方箋速查。
  * 嚴格落實法規合規，以「自然醫學調息」取代宣稱療效的醫療診斷語彙。
* 📲 **LINE 官方帳號與 LIFF 原生無縫整合**
  * 圖文選單點選文字即時辨識，後台回傳帶直跳按鈕之 Flex Message 卡片。
  * 支援短效 Opaque Handoff 憑證，防止體驗碼於 URL 或前台被篡改偽造。
* 🛡️ **頂級資安防禦與權限架構**
  * **反向代理真實 IP 辨識**：支援 Cloudflare 與 Render 多層代理標頭防偽。
  * **Stored XSS 防禦**：管理後台對預約人欄位全面採用純文字實體編碼跳脫。
  * **Edge Function 白名單驗證**：庫存同步函式嚴格校驗管理員 JWT 與資料表白名單。
* 📊 **行動友善日式管理後台**
  * **受付處（reception.html）**：預約清單、受付編號檢索、抽牌明細展開與處理狀態管理。
  * **庫存儀表板（inventory.html）**：瓶數即時統計、60 天效期預警、相機掃描條碼與 Google 試算表雙向同步。
  * **站點監控中心（sites.html）**：GitHub、Render、Vercel、Supabase 與 LINE Webhook 全站健康探測。

---

## 🏛️ 3. 五大 Agent 專業分工體系 (Five-Agent Architecture)

專案全面落實目錄級三權分立與五星專業分工，嚴禁越權跨目錄修改：

| 代理人角色 | 專屬目錄 | 職責與管轄範圍 |
| :--- | :--- | :--- |
| 🛡️ **Agent 1（後端工程師）** | [`/api/`](api/) | API 路由藍圖（`/health`, `/api/oils`, `/api/draws`）、LINE Webhook 簽章驗證、Supabase RPC 安全互動 |
| 🎨 **Agent 2（前端切版工程師）** | [`/components/`](components/) | 日式 UI 元件庫（側滑購物車 Drawer、首頁選品、圖鑑彈窗）、CSS 樣式表、發布目錄 [`/static/`](static/) |
| 🧪 **Agent 3（品管與測試工程師）** | [`/tests/`](tests/) | 12 大深度自動化測試套件（Testing Depth 2.0）、CI/CD 管線（`.github/workflows/`）、活體端點監控、零破圖與語法檢驗 |
| 📦 **Agent 4（商品與文案主編）** | [`/catalog/`](catalog/) | 131 款精油資料庫母體（`doterra.csv`）、單一建議零售價審查、自然醫學文案合規、同步工具（`sync_catalog.py`） |
| 💳 **Agent 5（維運與金流工程師）** | [`/infra/`](infra/) | 自訂獨立頂級網域 DNS 解析配置、Vercel / Render 規格、綠界 ECPay / LINE Pay 第三方線上金流架構 |

---

## 🛠️ 4. 技術架構

| 層級 | 使用技術 | 說明 |
| :--- | :--- | :--- |
| **前端 (Frontend)** | HTML5, Vanilla JavaScript (ES6+), CSS3 | 日式和紙侘寂風客製化樣式、LINESeedTW 官方字型、0.000 CLS 累積版面位移 |
| **後端 (Backend)** | Python 3.8+, Flask, Blueprint, LineBotSDK, Gunicorn | 模組化 API 藍圖、LINE Webhook 路由分發、短效 Opaque Token 防刷加密 |
| **商品母體 (Catalog)** | CSV, JSON 雙向同步 | `doterra.csv` 建議零售價與容量規範，自動編譯為前端高速 JSON |
| **維運金流 (Infra)** | DNS CNAME, ECPay, LINE Pay, SSL | 自訂網域解析指南、第三方金流閘道器架構與多雲配置 |
| **測試品質 (QA/CI)** | Python unittest, GitHub Actions, Node.js | 12 大深度測試套件矩陣（Testing Depth 2.0，78+ 項斷言）、持續整合 CI/CD 工作流、線上活體探測 |
| **資料庫 (Database)** | Supabase (PostgreSQL 15+) | RLS（Row Level Security）、SECURITY DEFINER 安全 RPC 函式、Check Constraints 約束 |

| **雲端部署 (Cloud)** | Vercel, Render | Vercel 託管靜態前端與邊緣快取；Render 託管 Python 後端 Web 服務 |

---

## 🚀 5. 安裝、測試與本地啟動

### 步驟 1：複製專案
```bash
git clone https://github.com/nm2y2nhwbm-hue/doterra.git
cd doterra
```

### 步驟 2：安裝依賴套件
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 步驟 3：設定環境變數
在專案根目錄建立 `.env` 檔案：
```env
CHANNEL_ACCESS_TOKEN="你的_LINE_CHANNEL_ACCESS_TOKEN"
CHANNEL_SECRET="你的_LINE_CHANNEL_SECRET"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"
```

### 步驟 4：執行完整自動化測試（Agent 3）
```bash
# 執行全套 34 項單元與整合測試
python -m unittest discover tests
```

### 步驟 5：商品資料庫同步（Agent 4）
```bash
# 每次修改 doterra.csv 後，編譯同步至前端 JSON
python catalog/sync_catalog.py
```

### 步驟 6：啟動本機伺服器
* **啟動後端服務（Agent 1）**：
  ```bash
  python line_bot.py
  # 健康檢查探測：http://localhost:5000/health
  # 精油資料庫：http://localhost:5000/api/oils
  ```
* **啟動前端靜態預覽（Agent 2）**：
  ```bash
  python -m http.server 8000 -d static
  # 瀏覽器造訪：http://localhost:8000/
  ```

---

## 📁 6. 資料夾結構說明

```text
doterra/
├── .github/workflows/         # 🧪 Agent 3: GitHub Actions CI/CD 自動化工作流
├── adapters/                  # 介面轉接層（LINE Flex Message 卡片轉譯）
│   └── line_adapter.py
├── api/                       # 🛡️ Agent 1: 後端 API 藍圖模組
│   ├── README.md              # Agent 1 守則與 API 協議
│   ├── __init__.py            # 匯出 api_bp 藍圖
│   └── routes.py              # 全站 API 路由（/health, /api/oils, /api/draws）
├── catalog/                   # 📦 Agent 4: 商品母體與內容審定目錄
│   ├── README.md              # Agent 4 定價容量與合規守則
│   └── sync_catalog.py        # 商品資料庫自動同步腳本
├── components/                # 🎨 Agent 2: 前端 UI 元件庫
│   ├── README.md              # Agent 2 元件規範
│   └── cart/                  # 日式側滑購物車（cart.css, cart.js）
├── core/                      # 系統核心商業邏輯
│   ├── database_manager.py    # 17 欄位精油母體安全讀取
│   ├── draw_logger.py         # 抽卡歷程安全日誌
│   └── experience_handoff.py  # 短效加密 Token 與 LINE 身分校驗
├── infra/                     # 💳 Agent 5: 維運與金流整合目錄
│   ├── README.md              # Agent 5 多雲與資安守則
│   ├── dns_custom_domain.md   # 自訂頂級網域 DNS 解析指南
│   └── payment_gateway_blueprint.md # 綠界 / LINE Pay 金流串接架構
├── static/                    # 🎨 Agent 2: 正式發布靜態目錄（Vercel 部署目標）
│   ├── index.html             # 官網首頁（含調息選品商城）
│   ├── cards.html             # 12 牌陣線上抽卡主頁
│   ├── oils.html              # 精油圖鑑 · 自然醫學調息全書
│   ├── booking.html           # 貴賓一對一預約表單
│   ├── reception.html         # 受付與抽牌紀錄後台
│   ├── inventory.html         # 精油庫存儀表板
│   ├── sites.html             # 站點健康監測中心
│   ├── oils-catalog.json      # 131 款建議零售價高速 JSON
│   ├── images/                # 品牌 Logo、卡牌與選品圖檔
│   └── fonts/                 # LINESeedTW 繁體中文 WebFont
├── supabase/                  # 資料庫 SQL 遷移紀錄與 Edge Functions
├── tests/                     # 🧪 Agent 3: 全套自動化測試目錄 (Testing Depth 2.0)
│   ├── README.md              # 測試指南、階梯架構與執行指令
│   ├── QA_COLLABORATION_MEMO.md # 跨 Agent 品質稽核與資安通報備忘錄
│   ├── run_all_tests.py       # 雙環境全量一鍵測試調度器
│   ├── test_api_endpoints.py  # 後端 API、防偽邊界與防回音測試
│   ├── test_payment_api.py    # 綠界 / LINE Pay 金流防偽強制重算測試
│   ├── test_security_audit.py # 全站資安照妖鏡、XSS 轉義與自然醫學法規測試
│   ├── test_experience_handoff.py# 短效 Token 加密與防刷邊界測試
│   ├── test_catalog_integrity.py # 建議零售價與官方規格完整性測試
│   ├── test_catalog_sync.py   # 目錄 CSV/JSON 1:1 精準映射測試
│   ├── test_asset_integrity.py# 全站靜態資產零破圖與日式美學規範測試
│   ├── test_live_endpoints.py # 線上生產環境活體探測
│   ├── test_js_syntax.js      # 全站 18 個 JS 模組 AST 語法編譯測試
│   ├── test_cart_logic.js     # 側滑購物車狀態單元測試
│   ├── test_cart_integration.js # 購物車與預約結帳合約整合測試
│   └── test_supabase_client.js# 前端 RPC 客戶端安全測試

├── AGENTS.md                  # 五大 Agent 職責邊界與開發憲法
├── doterra.csv                # 131 款現代精油核心資料庫（建議零售價、官方容量）
├── indicator_cards.csv        # 12 款指示卡元資料
├── line_bot.py                # 後端 Flask Webhook 主程式進入點
└── router.py                  # LINE 訊息文字意圖解析與分發路由
```

---

## ❓ 7. 常見問題 (FAQ)

### Q1：為什麼精油圖鑑與禮盒價格全面改為「單一建議零售價」？
> 為消滅過去雙軌定價（會員價／零售價標示不清）產生的困惑，全站 131 款精油與首頁 4 大禮盒全面對等台灣多特瑞官方之「單一建議零售價」，提供最透明、無爭議的消費與預約體驗。

### Q2：抽牌後的「體驗碼」如何防止偽造或外流？
> 系統廢棄了早期的 URL 參數傳遞體驗碼（experience_code），全面改採 **短效 Opaque Handoff 機制**：  
> 抽卡完成後只在伺服器端產生一組加密雜湊的短效憑證（有效期限 600 秒），使用者必須透過 LINE 登入／LIFF 驗證其真實身分後，才能解鎖並兌換真正的體驗碼。

### Q3：如何新增或修改精油資料？
> 任何精油資料異動由 **Agent 4** 專責：  
> 1. 編輯 `doterra.csv`（注意容量必須為 15ml / 5ml / 10ml 滾珠 / 115ml，價格必須為建議零售價正整數）。  
> 2. 執行 `python catalog/sync_catalog.py` 完成前端 JSON 編譯。  
> 3. 執行 `python -m unittest tests/test_catalog_integrity.py` 驗收法規合規性。

### Q4：網站文案與圖鑑內容是否有法規合規風險？
> 全站文案與 131 款精油處方箋，皆已嚴格依據台灣相關法規進行合規校正：全面去除「治療、抗炎、療效、處方」等具醫療診斷暗示之用語，統一代換為 **「自然醫學調息箋」、「身心校準」、「撫慰調適」**，兼顧專業深度與法律合規。

### Q5：五大 Agent 體系如何避免代碼衝突？
> 透過 [`AGENTS.md`](AGENTS.md) 嚴格定義目錄管轄邊界（`/api/`, `/components/`, `/tests/`, `/catalog/`, `/infra/`）。每位 Agent 僅能在專屬目錄下作業，無論在多分支平行開發或 AI 協同作業時，代碼衝突率均為 0%。

---

## 🤝 8. 貢獻與授權條款 (Contributing & License)

### 如何參與貢獻
1. **Fork 本專案** 至個人 GitHub 帳號。
2. 建立功能分支（`git checkout -b feature/amazing-feature`）。
3. 遵循 [`AGENTS.md`](AGENTS.md) 規範進行開發，並執行語法與安全性檢查。
4. 提交 Commit（`git commit -m 'feat: 新增特定牌陣支援'`）。
5. 推送至分支（`git push origin feature/amazing-feature`）並發起 **Pull Request**。

### 授權條款 (License)
本專案採 **MIT License** 授權開源，詳細條款請參閱根目錄之 [LICENSE](LICENSE) 檔案。  
*精油資料庫與「雫之洞悉 · 返魂堂」品牌識別著作權保留予原作者所有。*