# 💳 Agent 5：維運、自訂網域與金流整合目錄 (`/infra/`)

本目錄為 **Agent 5（維運與金流工程師）** 專屬管轄目錄，掌管多雲維運架構（Vercel、Render、Supabase）、自訂品牌頂級網域 DNS 解析、SSL 憑證管理，以及第三方線上金流閘道器（綠界科技 ECPay / LINE Pay）架構整合。

---

## 📌 負責職責

1. **自訂頂級網域與 DNS 維運**：
   * 指引自購頂級品牌網域（如 `yourbrand.tw`、`www.modernoilcards.com`）之 DNS CNAME / A 記錄配置。
   * 維護 Vercel 前端與 Render 後端自訂子網域 SSL 安全憑證輪替與 DNS 解析。
2. **多雲邊緣與運算規格維護 (Vercel & Render)**：
   * 制定 Vercel Edge Anycast CDN 快取政策、靜態檔案交付與安全性標頭（Security Headers）。
   * 制定 Render 後端 Python Web 服務規格、存活率健康監控與免費方案冷啟動（Spin-Down）防護。
   * 稽核 Supabase PostgreSQL RLS（資料列安全機制）與 Auth 憑證安全。
3. **第三方線上金流整合規格 (Payment Gateways)**：
   * 規劃與維護綠界科技（ECPay）信用卡／ATM／超商條碼支付協議與 CheckMacValue SHA256 驗簽。
   * 規劃與維護 LINE Pay v3 API 跨平台結帳整合與 HMAC-SHA256 標頭認證。
   * 定義訂單狀態機（Pending ➔ Paid ➔ Failed / Refunded）與伺服器端 Webhook 驗簽防禦。

---

## 📚 目錄架構與文件索引

* 🌐 [`dns_custom_domain.md`](dns_custom_domain.md)：品牌自訂頂級網域綁定與 DNS 解析設定實務手冊。
* ☁️ [`cloud_specs.md`](cloud_specs.md)：Vercel 前端邊緣 CDN 與 Render 後端容器運算規格書。
* 💳 [`payment_gateway_blueprint.md`](payment_gateway_blueprint.md)：綠界科技（ECPay）與 LINE Pay 線上支付串接架構藍圖。
* 🗄️ [`payment_schema_spec.sql`](payment_schema_spec.sql)：線上支付訂單表（`orders`）與稽核日誌（`payment_logs`）之 Schema 與 Supabase RLS 安全策略規格。
* 🔐 [`env_spec.md`](env_spec.md)：多雲環境變數配置清冊與金流金鑰安全規範。

---

## ⚠️ 邊界守則

* **嚴格邊界**：不得修改 `/components/` 前端 UI、`/api/` 業務端點、`/tests/` 測試套件與 `/catalog/` 商品文案。
* **零金鑰外洩**：任何金流密鑰（HashKey、HashIV、ChannelSecret）嚴禁硬編碼進程式碼中，必須透過環境變數安全注入。
