---
description: 測試案例規格 - 前端 Supabase RPC 客戶端安全 (supabase_client)
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在測試全數通過驗收後由流程更新。
> 測試類型：金鑰安全、就緒探測、抽卡交接、RPC 調用

---

## [x] 【金鑰安全】公開 Publishable Key 符合命名規範且無 Service Role 洩漏
**範例輸入**：檢驗 `OracleSupabase.SUPABASE_PUBLISHABLE_KEY`
**期待輸出**：格式符合 `sb_publishable_`，嚴禁外洩 service_role 秘密。

---

## [x] 【就緒探測】正確探測抽卡服務後端就緒狀態
**範例輸入**：調用 `oracle.getDrawApiReadiness()`
**期待輸出**：發起 GET 請求並解析回傳 `ready: true`。

---

## [x] 【抽卡交接】一般瀏覽器儲存抽卡僅保留 Handoff Token 不取得代碼
**範例輸入**：未登入 LINE 呼叫 `oracle.saveDrawAndGetCode(1, [], null)`
**期待輸出**：`lineVerified: false`、`code: null`，安全取得 `handoffToken`。

---

## [x] 【RPC 調用】建立預約時透過 Supabase RPC 安全生成受付編號
**範例輸入**：調用 `oracle.createBooking({ name: 'test' })`
**期待輸出**：回傳 `persisted: true`，且取得受付編號 `RCPT-001`。
