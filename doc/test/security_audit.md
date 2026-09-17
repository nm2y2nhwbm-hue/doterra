---
description: 測試案例規格 - 全站資安照妖鏡、XSS 注入防護與自然醫學法規邊界 (security_audit)
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在測試全數通過驗收後由流程更新。
> 測試類型：法規邊界、XSS 防禦、基建保溫、訂單持久化

---

## [x] 【法規邊界】檢驗商品資料母體絕對無衛福部管制之醫療療效與爭議詞彙
**範例輸入**：掃描 `doterra.csv` 與 `indicator_cards.csv` 全文
**期待輸出**：零違規詞彙，不包含「治療」、「治癒」、「消炎」、「抗癌」、「預防感冒」等管制詞彙。

---

## [x] 【XSS 防禦】確認 reception 管理後台 (admin.js) 具備 escapeHtml 與 sanitizeUrl 雙層防護
**範例輸入**：檢驗 `static/admin.js` 原始碼
**期待輸出**：包含 `escapeHtml` 與 `sanitizeUrl` 實體轉義過濾函式，杜絕 Stored XSS 與危險超連結跳轉。

---

## [x] 【XSS 防禦】確認 booking.js 表單與調息奉呈卡具備 escapeHtml 防護
**範例輸入**：檢驗 `static/booking.js` 原始碼
**期待輸出**：包含 `escapeHtml` 轉義函式，預防動態渲染顧客資料時被注入腳本。

---

## [x] 【XSS 防禦】確認 sites.js 服務監測儀表板具備 escapeHtml 與 sanitizeUrl 雙層防護
**範例輸入**：檢驗 `static/sites.js` 原始碼
**期待輸出**：包含 `escapeHtml` 與 `sanitizeUrl` 函式。

---

## [x] 【XSS 防禦】盤查 inventory.js 與 cart.js 的 innerHTML 轉義完整性
**範例輸入**：檢驗 `static/inventory.js` 與 `components/cart/cart.js` 原始碼
**期待輸出**：雙方皆明確定義並調用 `escapeHtml` 與 `sanitizeUrl`，防止 Stored/DOM-based XSS。

---

## [x] 【基建保溫】確認 keep_warm 預設使用 Render 外部 Ingress 網址維持活躍流量
**範例輸入**：檢驗 `core/keep_warm.py` 探測端點設定
**期待輸出**：探針目標非依賴本機 localhost，使用外部公開 Ingress 網址穿透負載平衡器。

---

## [x] 【訂單持久化】檢測金流訂單 Supabase 雙寫持久化防掉單機制
**範例輸入**：檢驗 `core/payment_manager.py` 訂單存取邏輯
**期待輸出**：包含 `_sync_order_to_supabase` 與 `_fetch_order_from_supabase` 雙寫與還原機制。
