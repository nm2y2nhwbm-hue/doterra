# 🎨 Agent 3：前端元件與頁面目錄 (`/components/`)

本目錄為 **Agent 3（前端切版工程師）** 專屬維護範圍，掌管所有前端 UI 元件、日式和色樣式、字型資產、靜態發布頁面，以及現代化 React 元件架構演進。

---

## 📌 負責職責

1. **核心 UI 元件庫 (Components Library)**：
   * `components/cart/`：全站日式側滑購物車（Cart Drawer）、懸浮角標、LocalStorage 狀態管理與即時總額運算。
   * `components/shop/`：首頁「調息香氣選品」4 大多特瑞官方建議零售價對等禮盒卡片。
   * `components/oils-catalog/`：131 款精油圖鑑 Modal、三大位格印章與自然醫學調息箋展開。
   * `components/navigation/`：頂部導覽列（含購物車按鈕）與頁尾水墨印章暗門。

2. **正式發布目錄 (`/static/`)**：
   * 負責 `static/` 下的 HTML5 頁面切版（`index.html`, `cards.html`, `oils.html`, `booking.html`, `admin.html`, `reception.html`, `inventory.html`, `sites.html`）。
   * 維護極致效能架構：LINESeedTW 字型非同步載入、圖片 85% 瘦身、0.000 版面位移（CLS）。
   * 全站落實 XSS `escapeHtml` 實體跳脫防護，徹底消除 Stored / DOM XSS 漏洞。

3. **日式款待美學 (Omotenashi UX)**：
   * 確保字距（`0.045em ~ 0.1em`）、行高（`1.9 ~ 2.0`）、蒔繪金箔細線（`#b8912e`）與柔和漫射光影（`--shadow-diffuse`）風格統一。

4. **⚛️ 現代 React (Vite + React + TypeScript) 元件架構演進藍圖**：
   * 對標林鼎淵（Dean Lin）《Vibe Coding Testing Practice》前端標準架構。
   * 演進目標：將原生 DOM 操作逐步升級為宣告式狀態管理元件（`<CartDrawer />`、`<OracleModal />`、`<BookingForm />`、`<DevPanel />`）。
   * 整合參考：對接 [`tests/reference/vibe-testing-practice/`](../tests/reference/vibe-testing-practice/) 內之 DevPanel 測試浮窗與路由守衛。

---

## ⚠️ 邊界守則

* **不得跨目錄修改** `/api/` 後端伺服器程式碼、`/tests/` 測試套件與 `/catalog/` 商品定價母體。
* 呼叫後端 API 必須遵循 Agent 1 與 Agent 2 訂定之協議合約（如 `GET /api/oils`、`POST /api/payments/create`）。