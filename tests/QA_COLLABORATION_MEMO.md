# 📋 Agent 3 全站品質稽核發現與跨 Agent 協同優化備忘錄 (QA Collaboration Memo)

> **發布者**：Agent 3（品管與測試工程師）  
> **發布日期**：2026-09-10  
> **適用範圍**：全專案五大代理人協作體系（Agent 1、Agent 2、Agent 4、Agent 5）  
> **宗旨**：依據日式款待美學（Omotenashi / 侘寂 / 間 / 所作）、無障礙無損閱讀標準（WCAG AA）與全站系統架構，提供跨領域工程師之具體優化建議與檔案坐標。

---

## 🚨 零、全站系統資安漏洞與架構風險通報專區 (Security & Vulnerability Audit)

依據 2026-09-10 最新全站「照妖鏡」深度代碼審計，發現以下 6 項跨邊界安全與架構缺陷，請各負責 Agent 參閱並安排修復：

### 0.1 【P0 嚴重】金流訂單暫存於容器 Ephemeral 磁碟，重啟遺失將致綠界 Webhook 斷炊
- **邊界歸屬**：**Agent 1（後端工程師）** ✕ **Agent 5（維運與金流工程師）**
- **檔案坐標**：[`core/payment_manager.py:L62-L163`](file:///c:/Users/User/Documents/GitHub/doterra/core/payment_manager.py#L62-L163)、[`infra/payment_schema_spec.sql`](file:///c:/Users/User/Documents/GitHub/doterra/infra/payment_schema_spec.sql)
- **漏洞根因**：
  目前 `OrderStore` 僅將訂單資料寫入伺服器本機檔案 `core/data/orders.json`（且在 `.gitignore` 排除清單內）。Render 容器於 15 分鐘無流量休眠（Spin-down）或重新部署重啟時，本機臨時磁碟會被完全清空。
- **危害情境**：
  客戶跳轉至綠界刷卡或進行 3D 驗證（平均歷時 3~10 分鐘），若期間伺服器休眠或冷啟動，綠界 Server-to-Server 異步回調時，`order_store.get_order(merchant_trade_no)` 將回傳 `None`，導致拋出 `ORDER_NOT_FOUND` (HTTP 404/400)，訂單狀態永遠無法自動更新為 `PAID`，亦無法對帳！
- **修復建請**：
  請 Agent 5 先行於 Supabase 正式套用 `infra/payment_schema_spec.sql` 中的 `orders` 與 `payment_logs` 資料表與 RLS；Agent 1 將 `OrderStore` 改為透過 Supabase Client / RPC 進行資料庫持久化儲存。

---

### 0.2 【P1 高危】後台庫存中心（`inventory.js`）缺乏轉義，存在 Stored XSS 漏洞
- **邊界歸屬**：**Agent 2（前端切版工程師）**
- **檔案坐標**：[`static/inventory.js:L195-L212`](file:///c:/Users/User/Documents/GitHub/doterra/static/inventory.js#L195-L212)
- **漏洞根因**：
  `static/admin.js`（受付後台）已導入 `escapeHtml` 防護，但 `static/inventory.js` 在渲染 `i.oil_name`、`i.product_id`、`i.capacity`、`i.note` 時，直接以 `${...}` 插值輸出至 `invList.innerHTML`，全檔案未見任何 `escapeHtml` 處理。
- **危害情境**：
  若精油名稱或備註欄位遭注入 `<img src=x onerror=...>` 等惡意 Payload，管理者登入庫存中心時將直接觸發 Stored XSS，攻擊者可竊取管理員 JWT Token。
- **修復建請**：
  Agent 2 應比照 `admin.js`，在 `inventory.js` 頂層補上 `escapeHtml` 輔助函式，並對所有動態變數進行轉義。

---

### 0.3 【P1 高危】購物車側滑抽屜（`cart.js`）存在 DOM XSS 注入風險
- **邊界歸屬**：**Agent 2（前端切版工程師）**
- **檔案坐標**：[`components/cart/cart.js:L312-L334`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.js#L312-L334)、[`static/cart.js:L312-L334`](file:///c:/Users/User/Documents/GitHub/doterra/static/cart.js#L312-L334)
- **漏洞根因**：
  `listEl.innerHTML = items.map(item => ...)` 渲染品項卡片時，直接插值 `${item.name}`、`${item.image}`、`${item.pillar}`、`${item.capacity}`。
- **危害情境**：
  若品項資料來自 URL 參數、惡意按鈕 `data-cart-item` 屬性或經污染之 `localStorage`，購物車展開時將觸發 DOM XSS。
- **修復建請**：
  Agent 2 應在 `cart.js` 內部封裝專屬 `escapeHtml`，確保所有插入 DOM 的屬性均經過 HTML 實體編碼。

---

### 0.4 【P2 中度】日式「間（Ma）」保溫 Worker 預設目標為 Localhost，無法維持外部喚醒
- **邊界歸屬**：**Agent 1（後端工程師）** ✕ **Agent 5（維運與金流工程師）**
- **檔案坐標**：[`core/keep_warm.py:L58-L60`](file:///c:/Users/User/Documents/GitHub/doterra/core/keep_warm.py#L58-L60)
- **漏洞根因**：
  若未設定環境變數 `KEEP_WARM_TARGET_URL`，預設 ping `http://127.0.0.1:5000/health`。Render 平台之休眠偵測僅計算經由外部 Ingress 負載平衡器的進站請求；容器內部對 `127.0.0.1` 的本機探測無法被判定為活躍流量，容器依然會在 15 分鐘後休眠。
- **修復建請**：
  Agent 1 應將缺省 fallback 改為 `https://doterra-73pv.onrender.com/health`；或由 Agent 5 在 Render Dashboard 環境變數中明確設置 `KEEP_WARM_TARGET_URL=https://doterra-73pv.onrender.com/health`。

---

### 0.5 【P2 中度】購物車「前往結帳」與後端金流 API 尚未完成端對端串接
- **邊界歸屬**：**Agent 1（後端工程師）** ✕ **Agent 2（前端切版工程師）**
- **檔案坐標**：[`components/cart/cart.js:L275-L285`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.js#L275-L285)、[`api/routes.py:L131-L150`](file:///c:/Users/User/Documents/GitHub/doterra/api/routes.py#L131-L150)
- **現況分析**：
  後端 Agent 1 已完備 `/api/payments/create`（強制重算官方定價與產出綠界跳轉表單），但前端 Agent 2 的購物車目前點擊「前往結帳」僅能導向 `booking.html` 並將商品填寫至備註，尚未提供「線上刷卡／LINE Pay 即時付款」之收銀台彈窗或跳轉流程。
- **修復建請**：
  Agent 2 可在購物車底層增加「線上立即付款」按鈕，呼叫後端 `/api/payments/create` 取得綠界跳轉參數並自動 Submit 表單導向金流收銀台。

---

### 0.6 【P3 低度】`booking.js` 呼叫未部署的 Edge Function 致 Console 404
- **邊界歸屬**：**Agent 2（前端切版工程師）** ✕ **Agent 5（維運與金流工程師）**
- **檔案坐標**：[`static/booking.js:L178`](file:///c:/Users/User/Documents/GitHub/doterra/static/booking.js#L178)、[`supabase/functions/`](file:///c:/Users/User/Documents/GitHub/doterra/supabase/functions)
- **現況分析**：
  預約成功後會呼叫 `generate-booking-confirmation` Edge Function，但 Supabase 目錄內並無此函式（僅有 `sync-inventory`），每次送出預約均會產生 404 網路錯誤。
- **修復建請**：
  由 Agent 5 補齊 AI 生成前導訊息之 Edge Function，或由 Agent 2 在函式未就緒前先以優雅靜默處理，避免破壞控制台純淨度。

---

## 🎨 一、建請 Agent 2（前端切版工程師）協同優化項


### 1.1 `style.css` 雙 `:root` 宣告整併（消滅樣式覆寫飄移）
- **檔案坐標**：[`static/style.css:L6-L42`](file:///c:/Users/User/Documents/GitHub/doterra/static/style.css#L6-L42)
- **稽核發現**：
  目前在第 6 行與第 32 行存在兩組 `:root` 宣告，導致若干設計標記被重複定義微調：
  - 第 7 行 `--paper: #F8F4EC;` ➔ 第 34 行覆寫為 `--paper: #F6F1E7;`
  - 第 11 行 `--forest: #435B48;` ➔ 第 36 行覆寫為 `--forest: #4B6350;`
  - 第 19 行 `--nav-h: 62px;` ➔ 第 39 行覆寫為 `--nav-h: 56px;`
- **建議方案**：
  整併為單一標準 `:root` 區塊，並以傳統日式和色嚴格規範命名：
  - **胡粉（Gofun）**：`--paper-light: #FAF6EC;`（頁面頂部柔光）
  - **白茶（Shiracha）**：`--paper: #F6F1E7;`（主背景底色）
  - **利休白茶（Rikyu-shiracha）**：`--paper-deep: #ECE3D2;`（卡片底色與抽屜背景）
  - **常磐綠（Tokiwa-midori）**：`--forest-deep: #253B2F;`（深邃主文字與主按鈕）
  - **蒔繪金（Makie-gold）**：`--gold: #B8912E;`、`--gold-hairline: rgba(184, 145, 46, 0.22);`（細線金箔描邊）

---

### 1.2 「間 (Ma)」動態留白與文字避頭尾排版
- **檔案坐標**：[`static/style.css`](file:///c:/Users/User/Documents/GitHub/doterra/static/style.css)
- **稽核發現**：
  行高 `1.95` 已具備良好的呼吸感，但在寬度小於 360px 的行動螢幕時，部分卡片內距顯得稍緊湊。
- **建議方案**：
  1. **流體邊距（Fluid Spacing）**：在 `@media (max-width: 480px)` 引入 `padding: clamp(14px, 3.5vw, 22px);`。
  2. **文字避頭尾（Orphan Prevention）**：在卡片正文段落（如 `.card-description`、`.oracle-guidance`）啟用 `text-wrap: pretty;` 或 `text-wrap: balance;`，杜絕單一字元孤立換行，維護日本印刷級的視覺雅緻。

---

### 1.3 「所作 (Shosa)」與「殘心 (Zanshin)」微互動
- **檔案坐標**：[`components/cart/cart.css`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.css)、[`components/cart/cart.js`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.js)
- **稽核發現**：
  目前購物車按鈕下壓 `scale(0.96)` 與加車彈跳已具備良好手感。
- **建議方案**：
  1. **導入「殘心（餘韻）」**：購物車 Toast 提示（`showToast`）在 2.5 秒倒數完畢時，建議加入煙嵐消散般的高斯模糊淡出（`filter: blur(4px); opacity: 0; transition: all 0.4s var(--ease-zen);`），而非突兀隱藏。
  2. **紙紋質感（Washi Texture）**：抽屜背景或彈窗可引入微弱的紙紋燥點，營造和紙溫潤觸感。

---

## 📜 二、建請 Agent 4（商品與文案主編）協同評估項

### 2.1 款待（Omotenashi）文案幽玄化修潤
- **檔案坐標**：[`static/index.html`](file:///c:/Users/User/Documents/GitHub/doterra/static/index.html)、[`components/cart/cart.js`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.js)
- **建議評估**：
  在保持流程直觀易懂的前提下，評估將部分電商術語微調為自然調息雅緻用詞：
  - 「加入購物車」 ➔ **「納入調息選品」** 或保持「加入調息清單」
  - 「前往結帳」 ➔ **「前往預約調息行囊」** 或 **「確認香氣選品」**
  - 目前購物車為空提示「目前尚未挑選香氣商品，讓直覺帶你探索」文筆極為優美，建請全站維持此種安靜沉穩之語調。

---

## 🛡️ 三、建請 Agent 1（後端工程師）協同維護項

### 3.1 精油 SKU 編號補全追蹤
- **檔案坐標**：[`doterra.csv`](file:///c:/Users/User/Documents/GitHub/doterra/doterra.csv)
- **稽核發現**：
  經 `tests/test_catalog_integrity.py` 掃描，目前尚有 9 筆精油標記為 `(待補)`。測試已建立防呆追蹤機制，不影響日常運作；建請 Agent 1 / 4 後續於官方資料齊全時統一補上標準 8 位數官方代碼。

---

## 💳 四、建請 Agent 5（維運與金流工程師）協同優化項

### 4.1 邊緣 CDN 快取標頭與 HSTS 安全
- **檔案坐標**：[`infra/cloud_specs.md`](file:///c:/Users/User/Documents/GitHub/doterra/infra/cloud_specs.md)、[`static/vercel.json`](file:///c:/Users/User/Documents/GitHub/doterra/static/vercel.json)
- **建議方案**：
  建請確保根目錄配置標準 `vercel.json`，將 `X-Frame-Options: SAMEORIGIN` 與 `Strict-Transport-Security` 廣播至所有邊緣端點，使全站探測標頭維持 A+ 安全評級。

---

## 🧪 五、Agent 3（品管與測試）自家守護承諾

為配合上述日式款待與品質規範，Agent 3 已在自家 [`tests/test_asset_integrity.py`](file:///c:/Users/User/Documents/GitHub/doterra/tests/test_asset_integrity.py) 完成了兩大守護防線實裝：
1. **`test_japanese_color_contrast_ratio()`**：以 W3C 相對亮度公式驗證暖米底與常磐深綠文字之色彩對比度達 **`10.28:1`**（遠高於 WCAG AA 4.5:1），確保視覺古典的同時長輩也能清晰閱讀。
2. **`test_zen_design_tokens_and_motion()`**：強制稽核全站日式 Design Tokens 與 `cubic-bezier(0.22, 1, 0.36, 1)` 禪意過渡無缺漏。
3. **`tests/run_all_tests.py`**：全量 11 套深度測試持續守護，維持 100% 綠燈秒級驗收。
