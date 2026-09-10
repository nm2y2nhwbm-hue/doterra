# AGENTS.md

## 適用範圍

本檔案適用於整個 `nm2y2nhwbm-hue/doterra` repository。開始工作前先閱讀本檔案；若未來子目錄另有 `AGENTS.md` 或 `AGENTS.override.md`，以較接近工作檔案的規則為優先。

## 五大 Agent 職責與目錄邊界（五星專業分工架構）

依據專案團隊升級規劃，專案劃分為五大獨立邊界目錄，各 Agent 嚴禁越權跨目錄修改：

1. **Agent 1 → `/api/`（後端工程師，當前助理專屬負責）**
   - **專屬負責目錄**：`/api/` 以及後端進入點 `line_bot.py` 的 Blueprint 註冊。
   - **職責**：Flask API 端點（`/health`, `/api/oils`, `/api/indicators`, `/api/draws`）、LINE Webhook 簽章校驗與分發、Supabase RPC 安全互動、安全 Token 防刷指紋與後端業務邏輯。
   - **嚴格守則**：專注後端邏輯與 `/api/` 目錄，**嚴禁修改前端 UI 元件 (`/components/`)、靜態切版 (`/static/`) 與測試 (`/tests/`)**。

2. **Agent 2 → `/components/`（前端切版工程師，由前端 Agent 專屬負責）**
   - **專屬負責目錄**：`/components/` 與發布目錄 `/static/`。
   - **職責**：日式美學 UI 元件（購物車 Cart Drawer、調息選品卡片、精油圖鑑彈窗、導覽列）、HTML5 頁面切版、CSS 樣式表、前端 JavaScript 互動邏輯。
   - **嚴格守則**：不修改後端伺服器邏輯 (`/api/`)、自動化測試 (`/tests/`) 與商品定價母體 (`/catalog/`)。

3. **Agent 3 → `/tests/`（品管與測試工程師，由測試 Agent 專屬負責）**
   - **專屬負責目錄**：`/tests/` 與 CI/CD 管線 (`.github/workflows/`)。
   - **職責**：單元測試、API 整合端點測試（`test_api_endpoints.py`）、交接 Token 安全校驗（`test_experience_handoff.py`）、資料庫與建議零售價完整性稽核（`test_catalog_integrity.py`）、線上活體端點驗證（`test_live_endpoints.py`）、前端元件與購物車邏輯驗證（`test_cart_logic.js`）、CI/CD 驗證與品質把關。
   - **嚴格守則**：專注於撰寫、維護測試套件與產出驗證報告，嚴禁跨目錄修改業務邏輯。

4. **Agent 4 → `/catalog/`（商品與文案主編，由內容 Agent 專屬負責）**
   - **專屬負責目錄**：`/catalog/` 與商品資料母體（`doterra.csv`, `indicator_cards.csv`）。
   - **職責**：131 款精油資料庫維護、官方單一建議零售價審定、官方標準容量（15ml / 5ml / 10ml 滾珠 / 115ml）、合規自然醫學文案把關（消滅醫療法規爭議詞彙）、商品圖鑑同步腳本（`sync_catalog.py`）。
   - **嚴格守則**：不更動前後端程式碼與測試套件，僅專注於資料母體與文案合規。

5. **Agent 5 → `/infra/`（維運與金流工程師，由維運 Agent 專屬負責）**
   - **專屬負責目錄**：`/infra/`。
   - **職責**：自訂獨立品牌頂級網域 DNS 解析配置、Vercel 邊緣 CDN 與 Render 伺服器規格、第三方線上金流閘道器（綠界 ECPay / LINE Pay）架構規格、Supabase RLS 與憑證安全管理。
   - **嚴格守則**：不修改核心業務 API 與前端樣式，任何金流密鑰嚴禁硬編碼。


## 專案目標與正式環境

- 品牌名稱：`現代精油心靈指引卡`。
- 英文副標：`MODERN OIL ORACLE`。
- GitHub repository：`nm2y2nhwbm-hue/doterra`。
- `main` 是唯一正式分支與 production source of truth。
- Vercel 前端：`https://doterra-two.vercel.app`。
- 正式預約頁：`https://doterra-two.vercel.app/booking.html`。
- Render 後端：`https://doterra-73pv.onrender.com`。
- Supabase 負責抽卡紀錄、預約、管理員權限、庫存與後台資料。
- LINE OA / LIFF 已接入既有流程；不要任意更換 ID、入口或 redirect 行為。

## 不可破壞的產品行為

1. 所有主要頁面維持「現代精油心靈指引卡」品牌名稱，並保留 `MODERN OIL ORACLE`。
2. 首頁「卡牌說明」必須直接在首頁開啟 modal，不可先導向 `cards.html`。
3. 網站有兩條正式抽卡入口，兩者都必須保留並分開驗證：
   - 瀏覽器介面入口：由 Vercel 首頁／一般瀏覽器進入 `cards.html`。
   - LINE OA 直達入口：由 LINE OA 的訊息或選單經 LIFF／LINE MINI App 直接進入 `cards.html` 與指定牌陣。
4. 一般瀏覽器完成抽卡後，不可直接顯示 `INSIGHT-...` 體驗碼；應先顯示 LINE / LIFF 入口，只有在 LINE / LIFF 驗證後才能顯示該次體驗碼。瀏覽器轉入 LINE 時必須維持同一次抽卡結果，不可默默要求重新抽卡，也不可把體驗碼直接放進 query parameter。
5. `booking.html` 完整預約表單與首頁簡易聯絡表單都必須透過 `OracleSupabase.createBooking()` → Supabase `create_booking` → `bookings` 儲存。
6. `admin.html` 是管理功能入口首頁，可顯示統計與模組入口，但不可重新放入詳細預約列表。
7. `reception.html` 專門呈現受付編號、預約名單、搜尋、狀態與抽牌結果。
8. `admin-home.js` 負責後台首頁登入、管理員權限檢查與統計；`admin.js` 負責 reception 詳細列表與狀態操作。
9. 抽卡分類「鏡子／河流／岔路」保持同一層並排；切換分類只更新下方子選單。
10. Reception 的單筆刪除只刪除預約並保留對應抽牌；「全部歸零」必須經確認文字與第二次確認，並清除 `bookings`、`draws`、`booking_counters`。

## 主要程式邊界

- `static/index.html`、`static/home.js`：首頁、分類入口與簡易聯絡表單。
- `static/cards.html`、`static/script.js`：抽卡主流程、LIFF 初始化、抽牌結果與體驗碼流程。
- `static/guide-modal.js`：首頁與抽卡頁共用的卡牌說明內容、dialog 語意、鍵盤與焦點管理。
- `static/site-fixes.js`：只負責在首頁初始化共用卡牌說明 modal。體驗碼 gate 應由 `static/script.js` 的單一流程負責，不要再加入 MutationObserver 或 query-parameter 解鎖補丁。
- `static/mode-catalog.js`：首頁與抽卡頁共用的分類／模式資料。
- `static/booking.html`、`static/booking.js`：正式預約表單。
- `static/supabase-client.js`：瀏覽器端 Supabase client、Render 抽牌交接 API 與 `create_booking` RPC 包裝；抽牌不可再由瀏覽器直接呼叫匿名 `save_draw`。
- `static/admin.html`、`static/admin-home.js`：管理入口、登入、權限與統計。
- `static/reception.html`、`static/admin.js`：受付與抽牌紀錄管理。
- `static/inventory.html`、`static/inventory.js`：庫存管理。
- `static/sites.html`、`static/sites.js`：production 與供應商狀態監測。
- `line_bot.py`：Flask / LINE webhook、Render health 與資料 API。
- `router.py`、`adapters/line_adapter.py`：LINE 文字路由與 LIFF 導流訊息。
- `core/`：卡片資料、資料庫讀取與抽牌記錄等核心模組。
- `supabase/`：目前的 SQL 建置腳本；不是完整 migration history。

## 工作前檢查

在修改前先執行並回報：

```powershell
git status --short --branch
git branch -a -vv
git log --oneline --decorate -n 10
```

- 確認目前 checkout、`main`、`origin/main` 與使用者指定的工作範圍。
- 保留使用者既有修改；不要覆蓋、回退或清理不屬於本次任務的變更。
- 先搜尋既有實作，尤其注意 `script.js` 與 `site-fixes.js` 的重複常數、資料與事件流程。
- 修改 production 行為前，先說明預計影響的頁面、資料流程與外部服務。

## 安全與外部服務限制

- 未經使用者明確授權，不得刪除 production 資料或建立測試預約／抽卡／管理員紀錄。
- 未經明確授權，不得修改 Supabase schema、RLS、grants、Auth 設定或執行 SQL migration。
- 不得把 Supabase `service_role`、LINE channel secret/access token 或其他秘密寫入前端、Git、log 或回覆。
- 未經明確授權，不得修改 LINE OA、LIFF ID、Render service、Vercel project 或 Supabase project。
- production smoke test 優先使用唯讀 GET；任何會建立資料、登入帳號、傳送 LINE 訊息或改變狀態的測試都要先取得授權。

## 驗證規則

專案已全面導入 **Testing Depth 2.0 深度自動化測試矩陣**（由 Agent 3 專責統籌），涵蓋 L1 語法層至 L6 統一調度層。提交前依規範執行檢查：

- **一鍵全量深度測試**：執行 `python tests/run_all_tests.py`，驗收全量 12 大深度測試套件（100% 綠燈）。
- **Git 完整性檢查**：所有變更執行 `git diff --check` 並檢視 `git diff --stat` 與完整 diff。
- **JavaScript 語法檢查**：`node tests/test_js_syntax.js`（遞迴掃描全站 18 個 JS 腳本 AST 語法）。
- **資安與法規邊界檢查**：`python -m unittest tests/test_security_audit.py`（XSS 轉義、雙寫持久化與自然醫學合規）。
- **Python 後端與金流檢查**：`python -m unittest tests/test_api_endpoints.py` 與 `python -m unittest tests/test_payment_api.py`。
- **HTML/CSS/瀏覽器流程修改後**：至少檢查首頁、`cards.html`、`booking.html`、`oils.html` 及受影響後台頁。
- **LINE／LIFF 修改**：必須分別驗證一般瀏覽器與 LINE App 雙環境，確認防回音攔截與自動回傳順暢。
- **Admin / reception / inventory 修改**：驗證未登入不顯示資料，登入後資料完全經由 `escapeHtml` 轉義防範 Stored XSS。
- **Production URL 或監測設定修改後**：確認 `static/sites.js` 以 `https://doterra-two.vercel.app/booking.html` 作為正式 booking URL。

## Git 與發布規則

- 不得自行 commit、push、merge、force-push、刪 branch 或直接改 GitHub 設定。
- 需要 Git 操作時，先向使用者列出預計執行的命令、分支、commit 範圍與 production 影響，取得確認後再執行。
- 發布前回報變更檔案、diff 摘要、已執行檢查、未驗證項目及 rollback 方式。
- 不得建立新的 Vercel project 或 Render service；沿用現有 production 資源。

## 目前已知待處理事項

以下是 2026-09-10 稽核與整改結果，開始工作前應重新確認現況：

- **LINE OA 抽卡防回音死循環**：已由 Agent 1 在 `router.py` 最前置攔截 `DRAW_RESULT_KEYWORDS`（體驗碼、INSIGHT-、牌陣結果）直接靜默返回 `None`；Agent 2 於 `script.js` 實現自動回傳與防手震；Agent 3 建立正反向控制整合測試（`test_line_webhook_echo_loop_prevention`）。
- **金流訂單 Supabase 雙寫持久化**：Agent 1 於 `core/payment_manager.py` 實裝 `_sync_order_to_supabase` 與 `_fetch_order_from_supabase`，訂單建立與付款狀態自動雙寫遠端 PostgreSQL，根除 Render 免費實例容器休眠臨時磁碟清空導致之掉單問題。
- **全站 XSS 實體轉義完備**：Agent 2 於 `static/inventory.js`、`components/cart/cart.js`、`static/cart.js` 全面導入 `escapeHtml` 與 `sanitizeUrl`；Agent 3 於 `test_security_audit.py` 實施永久強制斷言。
- **外部 Ingress 活躍保溫**：Agent 1 將 `core/keep_warm.py` 探測 fallback 提升為 Render 外部 Ingress 網址（`https://doterra-73pv.onrender.com/health`），真實穿透負載平衡器消除 15 分鐘冷啟動。
- **Testing Depth 2.0 全面落實**：全站具備 12 大深度自動化測試套件（78+ 項斷言）、統一調度器 `tests/run_all_tests.py` 與 GitHub Actions CI/CD 雙環境自動化管線。
