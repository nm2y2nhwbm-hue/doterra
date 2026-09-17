---
description: 測試案例規格 - 正式環境活體探測與網路韌性 (live_endpoints)
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在測試全數通過驗收後由流程更新。
> 測試類型：線上探測、CORS 與資安標頭、延遲評估

---

## [x] 【線上探測】探測 Render 後端 /health 與 /api/oils 正式端點
**範例輸入**：發送 HTTP GET 至 `https://doterra-73pv.onrender.com/health` 與 `/api/oils`
**期待輸出**：回傳 HTTP 200，服務狀態為 ok 且精油母體資料齊全。

---

## [x] 【線上探測】探測 Vercel 前端 8 大核心頁面存活
**範例輸入**：發送 HTTP GET 至 `index.html`, `cards.html`, `booking.html`, `oils.html`, `admin.html`, `reception.html`, `inventory.html`, `sites.html`
**期待輸出**：全數回傳 HTTP 200，頁面標題與品牌字串完整。

---

## [x] 【CORS 與資安標頭】檢驗線上 API 回應標頭安全性
**範例輸入**：檢驗 `/health` 與各 API 的回應標頭
**期待輸出**：包含正確之 Content-Type 與安全跨網域授權標頭。
