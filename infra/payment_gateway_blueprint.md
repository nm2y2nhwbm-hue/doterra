# 💳 第三方金流（綠界 ECPay / LINE Pay）串接架構藍圖 (`infra/payment_gateway_blueprint.md`)

本文件由 **Agent 5（維運與金流工程師）** 制定，明確規劃全站線上金流閘道器的串接架構、交易時序、API 規格、資安防禦機制，以及符合日式「おもてなし（款待美學）」之安心感結帳體驗規範，支援日式側滑購物車結帳。

---

## 🏗️ 一、系統交易時序圖 (Transaction Sequence)

```
[Agent 2: 前端日式購物車] ──(1. 提交商品清單與數量)──> [Agent 1: POST /api/orders]
                                                              │
                                                   (2. 查驗 doterra.csv 單一建議零售價)
                                                   (3. 建立訂單狀態: Pending)
                                                              │
                                                              ▼
[使用者瀏覽器] <──(4. 返回金流跳轉 HTML / 付款連結)── [綠界 ECPay / LINE Pay SDK]
      │                                                       │
      ▼ (進入 0.8s 日式款待過渡畫面)                          ▼
[跳轉至金流收銀台]                                    [金流處理授權 / 付款]
      │                                                       │
(5. 付款完成)                                                 │
      │                                                       ▼
      └─────────────────────────────────────────> (6. 異步 Webhook 通知伺服器)
                                                              │
                                                   (7. 驗簽 CheckMacValue / Hmac)
                                                   (8. 更新訂單狀態: Paid)
                                                              │
                                                              ▼
[使用者跳轉回官網款待致謝頁] <──(9. 查詢最新訂單狀態: Paid)── [Agent 1: GET /api/orders/:id]
```

---

## 🟢 二、綠界科技（ECPay）全方位金流規格

### 1. 支援支付方式
* 信用卡一次付清（含 3D 驗證）
* ATM 虛擬帳號轉帳
* 超商代碼／超商條碼繳費

### 2. 後端建立訂單參數 (AioCheckOut)
```json
{
  "MerchantID": "ECPAY_MERCHANT_ID",
  "MerchantTradeNo": "ORD20260910XXXX",
  "MerchantTradeDate": "2026/09/10 10:30:00",
  "PaymentType": "aio",
  "TotalAmount": 2450,
  "TradeDesc": "現代精油心靈指引卡選品結帳",
  "ItemName": "真正薰衣草 15ml x 1#野橘 15ml x 1",
  "ReturnURL": "https://doterra-73pv.onrender.com/api/payment/ecpay/callback",
  "ClientBackURL": "https://doterra-two.vercel.app/booking.html?payment=success",
  "ChoosePayment": "ALL",
  "EncryptType": 1
}
```

### 3. CheckMacValue 壓碼驗證演算法 (SHA256)
1. 將所有參數按照字典順序（A~Z）排序。
2. 參數前後分別加入 `HashKey={ECPAY_HASH_KEY}&` 與 `&HashIV={ECPAY_HASH_IV}`。
3. 進行 URL Encode（轉換為小寫，並遵循 .NET URL 編碼規則，如 `%20` ➔ `+`）。
4. 進行 SHA256 運算並轉為全大寫字串，比對回傳之 `CheckMacValue`。

---

## 🟢 三、LINE Pay 線上支付規格 (LINE Pay v3)

### 1. 核心 API 互動
* **付款請求 (Request API)**：`POST https://sandbox-api-pay.line.me/v3/payments/request`
  - 帶入 `orderId`、`amount`、`currency: "TWD"`、`confirmUrl`、`cancelUrl`。
  - 成功後取得 `web` 跳轉 URL，引導用戶在手機或桌面進行 LINE Pay 授權。
* **確認付款 (Confirm API)**：`POST https://sandbox-api-pay.line.me/v3/payments/{transactionId}/confirm`
  - 用戶授權完畢後，由後端發送 Confirm 扣款完成交易。

### 2. 標頭安全簽名 (HMAC-SHA256 Signature)
```http
Content-Type: application/json
X-LINE-ChannelId: {LINE_PAY_CHANNEL_ID}
X-LINE-Authorization-Nonce: {UUID / Timestamp}
X-LINE-Authorization: {Base64(HmacSHA256(ChannelSecret + URI + RequestBody + Nonce))}
```

---

## 🛡️ 四、Agent 5 訂立之資安防禦原則

1. **金額伺服器端重算 (Server-Side Price Validation)**：
   * 前端購物車傳入的商品 ID 與數量，後端（Agent 1）必須對照 `doterra.csv` 之官方建議零售價重新計算總額，**絕不信任前端傳來的單價或總金額**。
2. **防重放與冪等性防禦 (Idempotency)**：
   * 建立訂單與金流回調必須紀錄 `MerchantTradeNo` / `TransactionId`，若收到重複 Webhook 請求，直接返回成功 `1|OK`，不重複觸發庫存扣除。
3. **零金鑰外洩 (Zero Hardcoding)**：
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
  * 主標：*「正在為您連線至安全加密收銀台」*
  * 副標：*「256-bit SSL 傳輸加密保護 ‧ 為您妥善保存選品」*
* **防重送微互動 (Shosa 所作)**：
  * 按鈕立即轉為 Disabled 狀態，並開啟全螢幕防點擊遮罩，避免顧客焦慮連點造成重複發起多筆訂單。
  * 過渡停留時間設定為 **800ms ~ 1200ms**，提供適度呼吸感（間 Ma）後順暢跳轉至綠界或 LINE Pay。

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
