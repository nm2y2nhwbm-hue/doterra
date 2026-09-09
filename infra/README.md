# 💳 Agent 5：維運、自訂網域與金流整合目錄 (`/infra/`)

本目錄為 **Agent 5** 專屬維護範圍，掌管多雲維運架構（Vercel、Render、Supabase）、自訂品牌頂級網域 DNS 解析、SSL 憑證管理，以及第三方金流閘道器（綠界 ECPay / LINE Pay）架構整合。

---

## 📌 負責職責

1. **自訂頂級網域與 DNS 維運**：
   * 指引自購頂級品牌網域（如 `www.modernoilcards.com` 或自訂網域）之 DNS CNAME / A 記錄配置。
   * 維護 Vercel 前端與 Render 後端自訂子網域 SSL 安全憑證輪替。
2. **第三方線上金流整合 (Payment Gateways)**：
   * 規劃與維護綠界科技（ECPay）信用卡／ATM／超商條碼支付協議。
   * 規劃與維護 LINE Pay API 跨平台結帳整合。
   * 定義訂單狀態機（Pending ➔ Paid ➔ Failed / Refunded）與伺服器端 Webhook 驗簽安全防禦。
3. **多雲架構與環境變數維護**：
   * 監控 Vercel Edge CDN 快取標頭與安全性標頭。
   * 監控 Render 後端資源配置、Health 存活率與零中斷重啟。
   * 稽核 Supabase RLS（資料列安全機制）與 Auth 憑證安全。

---

## 📚 目錄文件索引

* [`dns_custom_domain.md`](dns_custom_domain.md)：品牌自訂頂級網域綁定與 DNS 解析設定實務手冊。
* [`payment_gateway_blueprint.md`](payment_gateway_blueprint.md)：綠界科技（ECPay）與 LINE Pay 線上支付串接規格架構書。

---

## ⚠️ 邊界守則
* **不得修改** `/components/` 前端 UI 與 `/api/` 業務端點，金流相關 API 異動需與 Agent 1 協同定義路由。
* 任何金流密鑰（HashKey、HashIV、ChannelSecret）嚴禁硬編碼進程式碼中，必須透過環境變數安全注入。
