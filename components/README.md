# 🎨 Agent 2：前端元件與頁面目錄 (`/components/`)

本目錄為 **Agent 2** 專屬維護範圍，掌管所有前端 UI 元件、互動邏輯、CSS 日式樣式、字型與靜態頁面。

---

## 📌 負責職責
1. **核心元件庫 (Components Library)**：
   * `components/cart/`：全站日式側滑購物車（Cart Drawer）、懸浮角標、LocalStorage 狀態管理。
   * `components/shop/`：首頁「調息香氣選品」4 大多特瑞對等禮盒卡片。
   * `components/oils-catalog/`：131 款精油圖鑑 Modal、三大位格印章與自然醫學調息箋展開。
   * `components/navigation/`：頂部導覽列（含購物車按鈕）與頁尾水墨印章暗門。
2. **正式發布目錄 (`/static/`)**：
   * 負責 `static/` 下的 HTML5 頁面切版（`index.html`, `cards.html`, `oils.html`, `booking.html`, `admin.html` 等）。
   * 維護極致效能架構：LINESeedTW 字型非同步載入、圖片 85% 瘦身、0.000 版面位移（CLS）。
3. **日式款待美學 (Omotenashi UX)**：
   * 確保字距（`0.045em ~ 0.1em`）、行高（`1.9 ~ 2.0`）、蒔繪金箔細線與柔和漫射光影風格統一。

---

## ⚠️ 邊界守則
* **不得修改** `/api/` 後端伺服器程式碼與 `/tests/` 測試腳本。
* 呼叫後端 API 必須遵循 Agent 1 訂定之協議（如 `GET /api/oils`、`POST /api/draws`）。