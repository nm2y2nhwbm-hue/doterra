---
description: 測試案例規格 - 短效 Token 防刷加密與雙入口狀態機 (experience_handoff)
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在測試全數通過驗收後由流程更新。
> 測試類型：設定就緒、憑證授權、狀態機轉換、防刷防偽

---

## [x] 【設定就緒】環境變數缺失時回報未就緒狀態 (503)
**範例輸入**：環境變數為空
**期待輸出**：回傳 HTTP 503 與 `not_configured` 狀態及缺失變數清單。

---

## [x] 【設定就緒】環境變數完整時回報就緒狀態 (200)
**範例輸入**：提供完整的 Supabase 與 LINE 密鑰變數
**期待輸出**：回傳 HTTP 200 與 `{"status": "ready"}`。

---

## [x] 【憑證授權】新版 Supabase Secret Key 不得作為 Bearer Token 送出
**範例輸入**：`sb_secret_example` 金鑰
**期待輸出**：`apikey` 標頭包含金鑰，且標頭中不得有 `Authorization: Bearer`。

---

## [x] 【憑證授權】舊版 Service Role Key 正確帶入 Bearer 標頭
**範例輸入**：`legacy-jwt` 金鑰
**期待輸出**：`apikey` 與 `Authorization: Bearer` 正確設定。

---

## [x] 【狀態機轉換】一般瀏覽器抽卡僅返回 Handoff Token 不得直接洩漏體驗碼
**範例輸入**：瀏覽器抽卡請求（未驗證 LINE ID Token）
**期待輸出**：回傳加密 `handoff_token`，`line_verified` 為 False，且回應中無 `code` 體驗碼。

---

## [x] 【狀態機轉換】LINE 驗證後抽卡直接核發體驗碼
**範例輸入**：附帶合法 LINE ID Token 之抽卡請求
**期待輸出**：伺服器驗證通過，`line_verified` 為 True，回傳正式 `INSIGHT-...` 體驗碼。

---

## [x] 【防刷防偽】憑證兌換還原原始抽牌結果
**範例輸入**：合法的使用者身分與 Token 兌換請求
**期待輸出**：精確回傳原始牌陣結果與體驗碼。
