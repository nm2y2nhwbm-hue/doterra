# AGENTS.md

## 適用範圍

本檔案適用於整個 `nm2y2nhwbm-hue/doterra` repository。開始工作前先閱讀本檔案；若未來子目錄另有 `AGENTS.md` 或 `AGENTS.override.md`，以較接近工作檔案的規則為優先。

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

本 repo 目前沒有統一的自動化測試套件。依修改範圍執行可用檢查並如實回報未能執行的項目：

- 所有變更至少執行 `git diff --check` 並檢視 `git diff --stat` 與完整 diff。
- JavaScript 修改後，若環境有 Node.js，對變更的 `.js` 檔執行 `node --check <file>`。
- Python 修改後，使用與 Render 相容的 Python 環境做語法／import 檢查；缺少 runtime 或 secrets 時不要假裝通過。
- HTML/CSS/瀏覽器流程修改後，至少檢查首頁、`cards.html`、`booking.html` 及受影響後台頁。
- LINE／LIFF 修改必須分別驗證一般瀏覽器與 LINE App；只檢查 DOM 不算完整 end-to-end 驗證。
- Admin / reception 修改需驗證未登入不顯示資料，並在有授權測試帳號時驗證 session、admin 白名單、列表讀取與狀態更新。
- Production URL 或監測設定修改後，確認 `static/sites.js` 以 `https://doterra-two.vercel.app/booking.html` 作為正式 booking URL。

## Git 與發布規則

- 不得自行 commit、push、merge、force-push、刪 branch 或直接改 GitHub 設定。
- 需要 Git 操作時，先向使用者列出預計執行的命令、分支、commit 範圍與 production 影響，取得確認後再執行。
- 發布前回報變更檔案、diff 摘要、已執行檢查、未驗證項目及 rollback 方式。
- 不得建立新的 Vercel project 或 Render service；沿用現有 production 資源。

## 目前已知待處理事項

以下是 2026-08-18 稽核結果，開始修復前應重新確認現況，完成後更新或移除本節：

- Production `main` 已移除 `experience_code` query 解鎖、第三方 QR、localStorage 自我解鎖及本機假體驗碼，並切換到安全抽卡交接 API。
- Supabase 已套用 `secure_draw_handoff`、外鍵索引與 `set_draw_code` schema-qualified trigger migration；後端與前端已發布短效交接 token、LINE ID Token 驗證及唯讀就緒檢查。真實 LINE OA／LIFF 手機重測仍是完成交接路徑的必要條件。
- 新流程正式驗證完成後，需另建 migration 撤銷 `anon`／`authenticated`／`public` 對舊 `save_draw` RPC 的執行權；不可在新後端上線前先撤銷，以免造成抽卡保存中斷。
- Supabase 從 `20260818015900_admin_reception_delete_reset.sql` 開始建立 migration history；更早的 schema 仍以既有 SQL 腳本為基準，並非完整歷史。
- Supabase 安全檢查仍有既有 SECURITY DEFINER、function search path 與 Auth 設定警告，未經授權不要擴大修正範圍。
- GitHub `main` 尚未啟用 branch protection 或 required status checks。
