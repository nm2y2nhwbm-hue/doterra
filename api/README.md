# 🛡️ Agent 1：後端服務與 API 目錄 (`/api/`)

本目錄為 **Agent 1（後端工程師）** 專屬維護範圍，掌管所有後端 API 端點、資料庫連線、LINE Webhook 接收、第三方金流核心與伺服器端資安防禦。

---

## 📌 負責職責與路由藍圖
1. **API 路由與協議**：
   * `GET /health`：後端存活探測（版本 `v2.3.0`）
   * `GET /api/keep-warm`：**「間（Ma）」** 心跳探測與守護保溫狀態端點
   * `GET /api/oils`：131 款精油資料庫讀取（容量與建議零售價）
   * `GET /api/indicators`：12 款指示卡資料庫讀取
   * `POST /api/log-draw`：抽卡歷程記錄
   * `GET /api/draws/health`：抽卡交接服務探測
   * `POST /api/draws`：抽卡紀錄防刷與短效加密 Handoff Token 發放
   * `POST /api/draws/redeem`：身分驗證與體驗碼兌換
   * `POST /api/payments/create`：建立付款訂單（商品金額伺服器端重算防偽）
   * `POST /api/payments/ecpay/callback`：綠界科技 ECPay 異步背景回調驗簽（`1|OK` 回應）
   * `GET /api/payments/status/<order_id>`：訂單付款狀態去敏查詢
2. **LINE Messaging API 整合**：
   * Webhook 簽章安全校驗（`X-Line-Signature`）與文字意圖分發
3. **第三方金流與交易防禦 (ECPay / LINE Pay)**：
   * 強制伺服器端根據 `doterra.csv` 及禮盒母體定價重新計價，嚴禁採信客戶端單價
   * 實作綠界 SHA256 `CheckMacValue` 演算法與異步回調驗證
   * 訂單狀態機（`PENDING` ➔ `PAID` / `FAILED`）與冪等性處理（防 Replay 重放）
4. **資料庫與資料處理**：
   * Supabase PostgreSQL RPC、RLS 白名單與資料完整性約束
   * CSV 資料庫讀取、清洗與結構化輸出
5. **安全防禦**：
   * Opaque Token 防偽、IP/User-Agent 限流指紋、CORS 全域安全跨域設定

---

## 🍵 日式職人款待精神升級 (Omotenashi & Craftsmanship)

依據專案日式美學規範，Agent 1 已完成五大後端架構升級：

1. **🍵 一、「丁寧さ（Teineisa）」—— 溫潤結構化 API 錯誤回饋**
   * 全面升級錯誤回傳結構：包含 `code`、`message`、`guidance`、`error` 四位一體溫潤語意。
   * 杜絕生硬技術報錯，提供清晰具體的引導說明。

2. **🛡️ 二、「気配り（Kikubari）」—— 對齊日本 APPI 標準之深度個資脫敏**
   * **姓名**：保留頭尾字元，中間全數掩碼（例如「王*明」、「歐**華」）。
   * **電話**：多段式掩碼保留前 4 碼與後 3 碼（例如「0912-***-456」）。
   * **Email**：保留前 2 碼與完整網域（例如「vi***@example.com」）。
   * **LINE ID**：保留前 2 碼與後 2 碼（例如「li***89」）。
   * **Zero-PII Logging**：後端 log 絕不記錄未去敏之顧客隱私。

3. **📜 三、「一期一會・殘心（Zanshin）」—— 訂單雅號與專屬調息籤條**
   * 訂單編號升級為日式雅號：`SHIZUKU-YYYYMMDDHHmmss-XXXX`（滴水穿石之禪意）。
   * 訂單建立與查詢自動注入依據選購精油位格（中柱/右柱/左柱）生成之 **當日調息籤條 (`zanshin_oracle`)**。

4. **⏳ 四、「間（Ma）」—— 消滅 Render 冷啟動延遲的預暖款待**
   * 實作 `core/keep_warm.py` 輕量背景守護 Worker 與 `GET /api/keep-warm` 端點。
   * 每 9 分鐘探測保溫，消滅免費用戶造訪時 30~50 秒之冷啟動等待。

5. **💳 五、「安心の証明（Trust Assurance）」—— 銀行級透明信任標章**
   * 訂單回傳附帶 SHA-256 驗證、官方母體定價驗證與 100% 正品承諾元資料 (`trust_assurance`)。

---

## ⚠️ 邊界守則
* **專屬負責**：`/api/`、後端進入點 `line_bot.py` Blueprint 註冊與 `core/` 運算防禦層。
* **嚴禁越權**：不得修改 `/components/`、`/static/`、`/catalog/`、`/tests/` 或 `/infra/`。
* **發布限制**：未經使用者明確確認授權，嚴禁私自執行 push。