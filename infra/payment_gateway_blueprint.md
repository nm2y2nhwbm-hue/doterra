# 💳 第三方金流（綠界 ECPay / LINE Pay）串接架構藍圖 (`infra/payment_gateway_blueprint.md`)

本文件由 **Agent 5（維運與金流工程師）** 制定，明確規劃全站線上金流閘道器的串接架構、交易時序、API 規格與資安防禦機制，支援日式側滑購物車結帳。

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
      ▼                                                       ▼
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
[使用者跳轉回官網成功頁面] <──(9. 查詢最新訂單狀態: Paid)── [Agent 1: GET /api/orders/:id]
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
