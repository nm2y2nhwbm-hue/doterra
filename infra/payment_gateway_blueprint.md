# 💳 第三方金流（LINE Pay v3 Sandbox 官方測試沙盒）串接架構藍圖 (`infra/payment_gateway_blueprint.md`)

本文件由 **Agent 5（維運與金流工程師）** 制定，明確規劃全站線上金流閘道器的串接架構、交易時序、API 規格、資安防禦機制，以及符合日式「おもてなし（款待美學）」之安心感結帳體驗規範。

> 📌 **重大架構宣告（2026-09-17）**：
> 1. **金流唯一通道定錨**：全站線上支付管道**唯一鎖定為 LINE Pay v3**，全面運作於 LINE Pay 官方測試沙盒（Sandbox）模式。
> 2. **舊渠道封存**：綠界科技（ECPay）渠道正式列為【封存 / Deprecated】，系統不再對外提供 ECPay 付款發起。
> 3. **無痛升級通道**：預留日後取得正式商業特店 Channel ID 後，僅需調整環境變數即可一秒無痛切換正式營運。

---

## 🏗️ 一、系統交易時序圖 (Transaction Sequence - LINE Pay v3)

```
[Agent 3: 前端日式購物車] ──(1. 提交商品清單與數量, provider='linepay')──> [Agent 2: POST /api/payments/create]
                                                                       │
                                                            (2. 查驗 doterra.csv 單一建議零售價重算)
                                                            (3. 強制雙寫 Supabase orders 表: PENDING)
                                                            (4. 呼叫 LINE Pay Request API 建立交易)
                                                                       │
                                                                       ▼
[使用者瀏覽器] <──(5. 返回 LINE Pay Web 跳轉付款連結)──────────────────┘
      │
      ▼ (進入 0.8s 日式款待過渡畫面：正在為您連線至 LINE Pay 安全收銀台)
[跳轉至 LINE Pay 收銀台] (https://sandbox-web-pay.line.me/...)
      │
      ▼ (6. 顧客在 LINE Pay 完成授權)
[LINE Pay 伺服器] ──(7. 授權完成，重新導向跳轉)──> [Agent 2: GET /api/payments/linepay/confirm]
                                                                       │
                                                            (8. 伺服器驗簽並發送 Confirm API 實質扣款)
                                                            (9. 更新 Supabase orders 表: PAID)
                                                            (10. 記錄 payment_logs 審計日誌)
                                                                       │
                                                                       ▼
[使用者跳轉回官網款待致謝頁] <──(11. 重新導向至 booking.html?payment=success&order_id=...)
```

---

## 🟢 二、LINE Pay 線上支付核心規格 (LINE Pay v3)

### 1. 環境通道切換規範 (Sandbox ➔ Production)
* **測試沙盒環境（預設啟用）**：
  * 環境變數：`LINE_PAY_STAGE=true`
  * API 網域：`https://sandbox-api-pay.line.me`
  * Web 付款收銀台：`https://sandbox-web-pay.line.me`
  * 預設沙盒測試金鑰（Fallback）：
    * `LINE_PAY_CHANNEL_ID`: `2000000000`
    * `LINE_PAY_CHANNEL_SECRET`: `mock-channel-secret-for-testing`
* **正式生產環境（商戶上線）**：
  * 環境變數：`LINE_PAY_STAGE=false`
  * API 網域：`https://api-pay.line.me`
  * Web 付款收銀台：`https://web-pay.line.me`

### 2. 核心 API 互動時序
* **付款請求 (Request API)**：`POST {BASE_URL}/v3/payments/request`
  - Request Body:
    ```json
    {
      "amount": 1845,
      "currency": "TWD",
      "orderId": "SHIZUKU-20260917-XXXX",
      "packages": [
        {
          "id": "PKG-1",
          "amount": 1845,
          "name": "現代精油心靈指引卡調息選品",
          "products": [
            {
              "id": "SET-MIRROR-01",
              "name": "【鏡子】當下覺察調息禮盒",
              "quantity": 1,
              "price": 1845
            }
          ]
        }
      ],
      "redirectUrls": {
        "confirmUrl": "https://doterra-73pv.onrender.com/api/payments/linepay/confirm",
        "cancelUrl": "https://doterra-two.vercel.app/#shop"
      }
    }
    ```
  - 成功回傳：包含 `info.paymentUrl.web` (桌面端) 與 `info.paymentUrl.app` (LINE App 直跳)，以及 `info.transactionId`。
* **確認付款 (Confirm API)**：`POST {BASE_URL}/v3/payments/{transactionId}/confirm`
  - 用戶授權完畢後，由後端發送 Confirm 扣款完成實質交易：
    ```json
    {
      "amount": 1845,
      "currency": "TWD"
    }
    ```
  - 成功回傳 `returnCode: "0000"`，更新訂單狀態為 `PAID`。

### 3. 標頭安全簽名 (HMAC-SHA256 Signature)
所有發送至 LINE Pay 之請求必須包含標準認證標頭：
```http
Content-Type: application/json
X-LINE-ChannelId: {LINE_PAY_CHANNEL_ID}
X-LINE-Authorization-Nonce: {UUID / Timestamp}
X-LINE-Authorization: {Base64(HmacSHA256(ChannelSecret + URI + RequestBody + Nonce))}
```
*註：GET 請求之簽名組成為 `ChannelSecret + URI + QueryString + Nonce`。*

---

## 📦 三、已封存金流渠道規格：綠界科技 (ECPay) [DEPRECATED]
> ⚠️ **狀態**：已封存（Archived / Deprecated）。後端一律拒絕 `provider='ecpay'` 之新發起訂單，歷史回調介面僅作相容性防禦保留。

---

## 🛡️ 四、Agent 5 訂立之資安防禦原則（含 Agent 3 照妖鏡稽核整改）

1. **金額伺服器端重算 (Server-Side Price Validation)**：
   * 前端購物車傳入的商品 ID 與數量，後端（Agent 1）必須對照 `doterra.csv` 之官方建議零售價重新計算總額，**絕不信任前端傳來的單價或總金額**。
2. **🚨 嚴禁本機磁碟暫存，強制 Supabase 資料庫持久化 (Zero Ephemeral Storage - 響應 Agent 3 第 0.1 項 P0 通報)**：
   * **缺陷防範**：Render 容器於休眠（Spin-down）或重新部署時，臨時檔案（如 `core/data/orders.json`）會被清空，導致綠界異步回調時遭遇 `ORDER_NOT_FOUND`。
   * **標準規範**：後端 `OrderStore` 嚴格禁止使用本機 JSON 檔案，必須全面介接 Supabase PostgreSQL 之 `public.orders` 與 `public.payment_logs` 資料表（定義於 [`infra/payment_schema_spec.sql`](payment_schema_spec.sql)）。保證訂單於容器重啟、休眠喚醒後 100% 可被綠界 Webhook 正確檢索與更新！
3. **防重放與冪等性防禦 (Idempotency)**：
   * 建立訂單與金流回調必須紀錄 `MerchantTradeNo` / `TransactionId`，若收到重複 Webhook 請求，直接返回成功 `1|OK`，不重複觸發庫存扣除。
4. **零金鑰外洩 (Zero Hardcoding)**：
   * 所有金流金鑰透過 Render 環境變數注入，禁止寫入任何程式碼或前端 Bundle。

---

## 🌸 五、おもてなし（款待美學）：結帳「安心感 UX」與優雅過渡規格

在日式頂級服務哲學中，結帳並非冷冰冰的資料傳輸，而是傳遞「安心、誠懇與守護」的款待儀態（おもてなし）。本章節訂立全站金流交互之體驗契約，供 Agent 1（後端錯誤處理）與 Agent 2（前端互動元件）協同對接。

### 1. 金流跳轉「款待過渡畫面」(Hospitality Transition Screen) 規格
當顧客於側滑購物車點擊「前往結帳」時，系統**絕不可直接突兀閃爍跳轉**，必須呈現優雅的品牌過渡層：
* **視覺氛圍**：
  * 背景採用日式半透明水墨遮罩（`rgba(248, 246, 240, 0.92)` 搭配 `backdrop-filter: blur(8px)`）。
  * 居中展示品牌水墨 Logo 與副標 `MODERN OIL ORACLE`。
* **安心引導文案**：
  * 主標：*「正在為您連線至 LINE Pay 安全收銀台」*
  * 副標：*「LINE Pay 官方安全傳輸加密 ‧ 為您妥善保存選品」*
  * 環境標記：*「[LINE Pay Sandbox 測試沙盒環境]」*（於沙盒模式明確標註，提升測試透明度）
* **防重送微互動 (Shosa 所作)**：
  * 按鈕立即轉為 Disabled 狀態，並開啟全螢幕防點擊遮罩，避免顧客焦慮連點造成重複發起多筆訂單。
  * 過渡停留時間設定為 **800ms ~ 1200ms**，提供適度呼吸感（間 Ma）後順暢跳轉至 LINE Pay 收銀台。

---

### 2. 安心感「溫潤日式異常引導矩陣」(Gentle Error Handling Matrix)
金流串接可能面臨發卡行拒絕、餘額不足或網路超時。日式款待準則**嚴禁向顧客呈現生硬技術代碼（如 `RtnCode: 10100058`、`CheckMacValue Fail`、`HTTP 500`）**，後端與前端必須依照下表將底層狀態轉換為溫和體貼的日式引導語：

| 底層錯誤情境 | 技術原始代碼範例 | 🚫 嚴格禁止顯示 | 🌸 日式安心感引導文案 (規範標準) |
| :--- | :--- | :--- | :--- |
| **卡片額度不足 / 扣款失敗** | `RtnCode: 10100058` / `Card Expired` | 交易失敗，信用卡錯誤 (10100058) | *「未能順利完成銀行授權。請確認卡片額度或效期，亦可為您切換至其他支付方式。」* |
| **3D 簡訊驗證逾時** | `OTP Timeout` / `Auth Cancelled` | 3D 驗證失敗，OTP 逾時 | *「驗證時間已超過。為守護您的帳戶交易安全，請重新點選發送驗證碼。」* |
| **連線延遲 / 金流逾時** | `Gateway Timeout` / `Connection Refused` | 連線中斷 504 Gateway Error | *「伺服器連線稍顯忙碌。我們已為您妥善保留選品清單，請稍候片刻再次嘗試。」* |
| **重複送出已完成訂單** | `Duplicate OrderNo` / `Already Paid` | 訂單已存在，無法重複支付 | *「此筆選品已於稍早完成結帳確認，感謝您的結緣，請無須重複付款。」* |
| **商品庫存臨時短缺** | `Insufficient Inventory` | 庫存不足，商品無法購買 | *「您所挑選的植萃精油此刻恰逢短缺，系統已為您更新購物車，敬請見諒。」* |

---

### 3. 款待致謝回條規格 (Post-Payment Hospitality Receipt)
顧客完成付款跳轉回官網時，呈現之訂單完成通知需具備儀式感：
* **訂單資訊透明**：清晰呈現訂單編號（`ORD...`）、付款方式（綠界信用卡 / LINE Pay）、結帳總額與購買品項。
* **款待結緣致謝語**：
  > *「感謝您與植物香氣的相遇。每一滴精油，都將帶著大地的祝福送到您的身邊。我們正細心為您揀選與包裝。」*
* **LINE 狀態推播銜接**：若該訂單帶有 `line_user_id`，同步觸發 LINE Messaging API 發送「出貨通知與款待回條」Flex Message，實現全方位無縫安心感。
