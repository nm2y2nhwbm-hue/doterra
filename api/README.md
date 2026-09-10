# 🛡️ Agent 1：後端服務與 API 目錄 (`/api/`)

本目錄為 **Agent 1** 專屬維護範圍，掌管所有後端 API 端點、資料庫連線、LINE Webhook 接收與伺服器端資安防禦。

---

## 📌 負責職責
1. **API 路由與協議**：
   * `GET /health`：後端存活探測
   * `GET /api/oils`：131 款精油資料庫讀取（容量與建議零售價）
   * `GET /api/indicators`：12 款指示卡資料庫讀取
   * `POST /api/log-draw`：抽卡歷程記錄
   * `GET /api/draws/health`：抽卡交接服務探測
   * `POST /api/draws`：抽卡紀錄防刷與短效加密 Handoff Token 發放
   * `POST /api/draws/redeem`：身分驗證與體驗碼兌換
   * `POST /api/payments/create`：建立付款訂單（商品金額伺服器端重算防偽）
   * `POST /api/payments/ecpay/callback`：綠界科技 ECPay 異步背景回調驗簽（1|OK 回應）
   * `GET /api/payments/status/<order_id>`：訂單付款狀態去敏查詢
2. **LINE Messaging API 整合**：
   * Webhook 簽章安全校驗（`X-Line-Signature`）與文字意圖分發
3. **第三方金流與交易防禦 (ECPay / LINE Pay)**：
   * 強制伺服器端根據 `doterra.csv` 及禮盒母體定價重新計價，嚴禁採信客戶端單價
   * 實作綠界 SHA256 `CheckMacValue` 演算法與異步回調驗證
   * 訂單狀態機（PENDING ➔ PAID / FAILED）與冪等性處理（防 Replay 重放）
4. **資料庫與資料處理**：
   * Supabase PostgreSQL RPC、RLS 白名單與資料完整性約束
   * CSV 資料庫讀取、清洗與結構化輸出
5. **安全防禦**：
   * Opaque Token 防偽、IP/User-Agent 限流指紋、CORS 全域安全跨域設定

---

## ⚠️ 邊界守則
* **不得修改** `/components/` 與 `static/` 下的前端 UI 切版與頁面樣式。
* 任何對外 API 異動均需保持向下相容性或同步更新版本號。