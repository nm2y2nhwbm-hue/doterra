# 🔐 雲端環境變數與金流金鑰安全規範 (`infra/env_spec.md`)

本文件由 **Agent 5（維運與金流工程師）** 制定，為專案唯一環境變數注入與安全標準依據。

---

## ⚠️ 資安最高指導原則

1. **嚴禁程式碼寫死 (Zero Hardcoding)**：所有金流 HashKey、HashIV、ChannelSecret、Supabase Service Role Key 絕不可提交至 Git 或出現在前端 JS。
2. **最小權限原則**：前端 Vercel 僅注入唯讀或受 RLS 保護的 Public Anon Key；高權限與驗簽金鑰僅限 Render 後端容器。

---

## 📋 環境變數配置清冊

### 1. Render 後端環境變數 (Backend - API & Payment Webhook)

| 變數名稱 | 敏感等級 | 範例 / 格式 | 用途說明 |
| :--- | :---: | :--- | :--- |
| `PORT` | 低 | `10000` | Render 監聽通訊埠 |
| `FLASK_ENV` | 低 | `production` | Flask 運行模式 |
| `LINE_CHANNEL_SECRET` | 🔴 極高 | 32 位元十六進位字串 | LINE Webhook 簽章校驗 (HMAC-SHA256) |
| `LINE_CHANNEL_ACCESS_TOKEN` | 🔴 極高 | 長字串 (Channel Access Token) | LINE Messaging API 發布推播訊息 |
| `LIFF_ID` | 中 | `2006...-xxxx` | LINE LIFF 應用程式唯一代碼 |
| `SUPABASE_URL` | 中 | `https://xxxx.supabase.co` | Supabase 專案 API URL |
| `SUPABASE_KEY` | 🔴 極高 | JWT (service_role 或 server anon) | 後端安全資料庫操作憑證 |
| `ECPAY_MERCHANT_ID` | 中 | `3002607` (測試) / 7位數字 | 綠界特店編號 |
| `ECPAY_HASH_KEY` | 🔴 極高 | `pwFHCqoQZGmho4w6` (測試) | 綠界交易壓碼 HashKey (SHA256) |
| `ECPAY_HASH_IV` | 🔴 極高 | `EkRm7iFT261dpevs` (測試) | 綠界交易壓碼 HashIV (SHA256) |
| `LINE_PAY_CHANNEL_ID` | 中 | 10位數字 | LINE Pay 商家 Channel ID |
| `LINE_PAY_CHANNEL_SECRET` | 🔴 極高 | 32 位元字串 | LINE Pay 請求標頭 HMAC-SHA256 簽名密鑰 |

---

### 2. Vercel 前端環境變數 (Frontend - Edge CDN)

| 變數名稱 | 敏感等級 | 範例 / 格式 | 用途說明 |
| :--- | :---: | :--- | :--- |
| `NEXT_PUBLIC_SUPABASE_URL` | 公開 | `https://xxxx.supabase.co` | 瀏覽器直連 Supabase API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | 公開受限 | JWT (anon public) | 受 RLS 限制之客戶端公鑰 |
| `NEXT_PUBLIC_API_BASE_URL` | 公開 | `https://doterra-73pv.onrender.com` | 後端 API 根端點（支援自訂 api 網域） |
| `NEXT_PUBLIC_LIFF_ID` | 公開 | `2006...-xxxx` | LIFF SDK 初始化識別碼 |
