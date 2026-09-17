---
description: 測試案例規格 - 後端 API 路由完整性與安全防護 (api_endpoints)
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在測試全數通過驗收後由流程更新。
> 測試類型：API 規格、健康探測、抽卡事件、防禦邊界、代理防護、防回音循環

---

## [x] 【API 規格】測試 /health 健康檢查端點（回傳版本、服務名稱與品項統計）
**範例輸入**：HTTP GET `/health`
**期待輸出**：回傳 HTTP 200，JSON 包含 `status: "ok"`、`service: "modern-oil-oracle-api"`，且 `catalog_items >= 60`。

---

## [x] 【API 規格】測試 /api/oils 精油資料庫端點（驗證容量與建議零售價映射）
**範例輸入**：HTTP GET `/api/oils`
**期待輸出**：回傳 HTTP 200，資料為清單且筆數 `>= 60`，每筆包含 `id`, `name`, `name_en`, `guidance`, `chakra`, `price_retail` (正整數), `capacity`。

---

## [x] 【API 規格】測試 /api/indicators 回傳指示卡資料庫
**範例輸入**：HTTP GET `/api/indicators`
**期待輸出**：回傳 HTTP 200，資料為清單且筆數 `>= 12`，包含 `id`, `name`。

---

## [x] 【健康探測】測試 /api/draws/health 抽卡服務探測端點
**範例輸入**：HTTP GET `/api/draws/health`
**期待輸出**：回傳 HTTP 200 或 503，JSON 包含 `status` 欄位。

---

## [x] 【抽卡事件】測試 /api/log-draw POST 抽卡事件記錄
**範例輸入**：HTTP POST `/api/log-draw` 傳入 `{"user_id": "test-user-001", "display_name": "測試使用者", "mode": "mirror", "cards": ["乳香", "安定平衡"]}`
**期待輸出**：回傳 HTTP 200，JSON 包含 `"success": true`。

---

## [x] 【防禦邊界】測試 /api/draws 建立抽卡紀錄於空負載時的安全拒絕 (400)
**範例輸入**：HTTP POST `/api/draws` 傳入空 JSON `{}`
**期待輸出**：回傳 HTTP 400/422/500，且 `persisted` 為 False。

---

## [x] 【防禦邊界】測試 /api/draws/redeem 兌換無效或竄改之 Token 安全阻斷
**範例輸入**：HTTP POST `/api/draws/redeem` 傳入竄改之 Token 與假 ID Token
**期待輸出**：安全阻斷，回傳錯誤狀態碼且 `persisted` 為 False。

---

## [x] 【代理防護】測試反向代理客戶端 IP 辨識優先級 (CF-Connecting-IP > X-Real-IP > X-Forwarded-For)
**範例輸入**：帶有 `CF-Connecting-IP`, `X-Real-IP`, `X-Forwarded-For` 之多層反向代理請求
**期待輸出**：精確遵循 Cloudflare 優先辨識客戶端真實 IP。

---

## [x] 【防回音循環】防回音與訊息路由測試案例：包含抽卡結果關鍵字靜默攔截與正規選單正向回傳
**範例輸入**：1. 使用者回傳包含「體驗碼」、「INSIGHT-」、「牌陣」等抽卡結果文字；2. 使用者點擊「今日能量」、「鏡子」、「河流」、「岔路」
**期待輸出**：1. 路由靜默攔截回傳 None（消滅回音死循環）；2. 正向對照組正常回傳引導卡片訊息。
