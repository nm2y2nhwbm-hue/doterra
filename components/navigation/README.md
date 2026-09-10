# 🧭 導覽與頁尾元件 (`components/navigation/`)

本目錄為 **Agent 2（前端切版工程師）** 負責維護之頂部款待導覽列（含購物車抽屜呼叫與動態角標）及頁尾水墨印章管理暗門。

---

## 📌 元件清單
- **`nav.html`**：頂部固定毛玻璃導覽列與頁尾日式款待品牌落款結構。
- **`nav.css`**：毛玻璃背景 (`backdrop-filter`)、蒔繪金線底邊、iOS Safe Area 頂部適配、購物車角標與行動版自適應排版。

---

## 🍵 款待美學與無障礙規格 (Omotenashi Specs)

1. **極致手感與安全區域**：
   - 頂部導覽列支援 `env(safe-area-inset-top, 0px)`，完美避開 iPhone 動態島與瀏海屏。
   - 頁尾支援 `env(safe-area-inset-bottom, 0px)`，防止與 Home 指示條產生遮擋。
2. **購物車動態聯動**：
   - 帶有 `.nav-cart-link` 類別之按鈕會在點擊時自動開啟日式購物車抽屜。
   - 內含 `.nav-cart-count` 元素，當 `cart:updated` 事件廣播時，自動同步顯示目前調息選品總數量。
3. **頁尾水墨印章暗門**：
   - 頁尾品牌標誌連結連往 `admin.html`，具備 `aria-label` 標註，提供管理員隱密、低干擾的後台入口。
