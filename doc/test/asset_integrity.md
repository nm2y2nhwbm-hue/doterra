---
description: 測試案例規格 - 全站靜態資源、圖檔路徑與資產一致性 (asset_integrity)
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在測試全數通過驗收後由流程更新。
> 測試類型：資產完整性、靜態連結、代碼一致性

---

## [x] 【資產完整性】驗證 doterra.csv 中所有精油實體圖檔皆存在於 static/images/
**範例輸入**：讀取 `doterra.csv` 之 `image_filename`
**期待輸出**：所有精油圖檔皆存在於 `static/images/`，零破圖。

---

## [x] 【資產完整性】驗證 indicator_cards.csv 中所有指示卡圖檔皆存在於 static/images/
**範例輸入**：讀取 `indicator_cards.csv` 之 `image_filename`
**期待輸出**：所有指示卡圖檔皆存在於 `static/images/`。

---

## [x] 【靜態連結】驗證所有 HTML 檔案中引用的本機圖檔、樣式與腳本皆存在 (零 404)
**範例輸入**：掃描所有 `static/*.html` 的 `src` 與 `href` 本機參照
**期待輸出**：所有引用的資源檔案真實存在，無死連結。

---

## [x] 【代碼一致性】驗證 components/cart/ 與 static/ 購物車代碼 100% 一致
**範例輸入**：比對 `components/cart/cart.js` 與 `static/cart.js`、`components/cart/cart.css` 與 `static/cart.css`
**期待輸出**：內容 100% 位元一致。
