# Site Architecture: 雫之洞悉 · 返魂堂 (現代精油心靈指引卡)
**Stitch Project ID:** 5923035553865007790

## 1. Site Vision
「雫之洞悉 · 返魂堂」是一套結合精油心靈指引、三位格牌陣、日式和風籤詩與現代芳香療癒選品的全方位數位款待體驗。為現代人提供 3 分鐘深層覺察、牌卡占卜引導、個人化精油預約體驗與 LINE Pay 沙盒一鍵結帳服務。

## 2. Technical Stack
* **Frontend:** HTML5, CSS3 (Wabi-sabi Zen), JavaScript (ES2022+), Vite + React Components (Roadmap)
* **Backend:** Python 3.13 Flask (Render API), LINE Messaging API Webhook
* **Database & Auth:** Supabase PostgreSQL, RPC Transactions, RLS Policies, Row Locks
* **Payments:** LINE Pay v3 Sandbox (HMAC-SHA256, `LINE_PAY_STAGE=true`)
* **Design Engine:** Google Stitch MCP Integration (`5923035553865007790`)

## 3. Stitch Project Integration
* **Project Name:** 雫之洞悉 · 返魂堂 - Sync
* **Resource ID:** `projects/5923035553865007790`
* **Sync Mode:** Dual-sync (DOM & Design System reverse-engineered to Stitch)

## 4. Current Sitemap & Core Screens
1. **Home (`index.html`):** 首頁儀表板，涵蓋 Hero 禪意大景、牌陣分類導覽（鏡子 / 河流 / 岔路）、4 大調息禮盒選品櫥窗、簡易聯絡奉呈與卡牌說明 Modal。
2. **Oracle Cards (`cards.html`):** 線上抽牌儀式核心，支援牌陣洗牌、翻牌動態、牌義籤詩解讀、四字熟語、LINE 體驗碼 (`INSIGHT-...`) 安全認證。
3. **Booking Form (`booking.html`):** 貴賓預約奉呈卡，整合時段預約、調息選品帶入、LINE Pay 沙盒安全結帳跳轉。
4. **Oil Catalog (`oils.html`):** 131 款多特瑞精油百科，三柱位格分類（中柱平衡 / 左柱陰柔 / 右柱陽剛）、脈輪能量檢索與詳細調息彈窗。
5. **Cart Drawer & Dedicated Management Panel (`cart.html` / `components/cart/`):** 購物車專屬管理面板與右側滑出抽屜，具備 4 大指標卡片、即時金額防偽重算、水滴空狀態與款待過渡畫面（`linepay-transition-overlay`）。

## 5. Stitch Loop Roadmap
* [x] **Sprint 1 (Baseline Sync):** 現有 DOM 與 CSS 視覺系統逆向工程至 Stitch，綁定 Project ID `5923035553865007790`。
* [x] **Sprint 2 (Cart Portal):** 透過 Stitch Loop 完成「購物車專屬管理面板 (`cart.html`)」，支援雙向數據響應與 LINE Pay 一鍵結帳。
* [ ] **Sprint 3 (Daily Fortune):** 依據 `.stitch/next-prompt.md` 擴充「每日能量籤詩占卜與身心調息 (fortune-teller.html)」。
* [ ] **Sprint 4 (React Migration):** 運用 `stitch-build:react-components` 將日式購物車與預約卡牌轉譯為 React TSX 元件。
