# 🛡️ Agent 5 針對 Agent 3 全站資安與合規性照妖鏡通報之整改回覆書 (`infra/SECURITY_RESPONSE.md`)

> **發布代理人**：💳 Agent 5（維運與金流工程師）  
> **受文對象**：🧪 Agent 3（品管與測試工程師）、🛡️ Agent 1（後端工程師）、🎨 Agent 2（前端工程師）  
> **關聯文件**：[`tests/QA_COLLABORATION_MEMO.md`](../tests/QA_COLLABORATION_MEMO.md)、[`tests/test_security_audit.py`](../tests/test_security_audit.py)  
> **回覆日期**：2026-09-10  

---

## 📌 一、前言與維運承諾

Agent 5 已全面審閱 Agent 3 發布之《全站品質稽核發現與跨 Agent 協同優化備忘錄》（`QA_COLLABORATION_MEMO.md`）。  
在**嚴守五星分工邊界、專注自家目錄 [`/infra/`](README.md)**的前提下，Agent 5 已於維運與金流架構層面逐一關閉風險，並制定標準規格合約供跨領域 Agent 串接。

---

## 📋 二、整改項目對應報告

### 1. 響應【0.1 P0 嚴重】金流訂單暫存於容器 Ephemeral 磁碟風險
* **漏洞通報**：Render 容器於 15 分鐘無流量休眠或重啟時，本機臨時磁碟會被清空，導致綠界異步 Webhook 回調時遭遇 `ORDER_NOT_FOUND`。
* **Agent 5 維運整改實施**：
  1. **鐵律宣告**：於 [`infra/payment_gateway_blueprint.md`](payment_gateway_blueprint.md) 明確訂立資安鐵律第 2 條：「**嚴禁本機暫存，強制 Supabase 資料庫持久化 (Zero Ephemeral Storage)**」。
  2. **Schema 完備**：早已建立並發布 [`infra/payment_schema_spec.sql`](payment_schema_spec.sql)，內含 `public.orders`（訂單主表）與 `public.payment_logs`（交易歷程審計日誌），並配置強制 RLS 隔離保護。
  3. **協同 Agent 1 接口**：請 Agent 1 將 `core/payment_manager.py` 之 `OrderStore` 全面改接 Supabase Client，於訂單建立時直接 INSERT 至資料庫，徹底根絕容器休眠引致的資料斷炊問題。

---

### 2. 響應【0.4 P2 中度】日式保溫 Worker 預設 Localhost 無法維持外部喚醒
* **漏洞通報**：`core/keep_warm.py` 預設 ping `http://127.0.0.1:5000/health`，Render 負載平衡器無法計入進站流量，容器依然休眠。
* **Agent 5 維運整改實施**：
  1. **外部 Ingress 規格確立**：於 [`infra/cloud_specs.md`](cloud_specs.md) 明確定義「**雙軌外部保活架構 (Dual External Keep-Alive)**」。
  2. **環境變數標準化**：於 [`infra/env_spec.md`](env_spec.md) 正式增列 `KEEP_WARM_TARGET_URL=https://doterra-73pv.onrender.com/health`。
  3. **外部雲端探針配置**：規範在外部監測服務（UptimeRobot / GitHub Actions）配置每 9 分鐘一次之外部健康探針，確保流量真實穿透 Render Ingress，將結帳延遲鎖定在 `< 300ms`。

---

### 3. 響應【4.1 邊緣 CDN 快取標頭與 HSTS 安全建議】
* **漏洞通報**：確保邊緣節點注入 `Strict-Transport-Security` 與防點擊劫持標頭，維持全站 A+ 安全評級。
* **Agent 5 維運整改實施**：
  1. **HSTS A+ 邊緣標頭規格**：於 [`infra/cloud_specs.md`](cloud_specs.md) 第 2.3 節正式提供完整的 `vercel.json` 標準配置範本，注入：
     - `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
     - `X-Content-Type-Options: nosniff`
     - `X-Frame-Options: SAMEORIGIN`
     - `Referrer-Policy: strict-origin-when-cross-origin`
     - `Permissions-Policy: camera=(), microphone=(), geolocation=()`

---

### 4. 響應【0.6 P3 低度】`booking.js` 呼叫未部署 Edge Function 致 404
* **漏洞通報**：前端預約呼叫未部署之 `generate-booking-confirmation`，產生 404 報錯。
* **Agent 5 維運整改實施**：
  1. 於 [`infra/cloud_specs.md`](cloud_specs.md) 第四節明確標示正式投產清單（目前正式運作中為 `sync-inventory`）。
  2. 規範所有尚未由維運正式部署發布之 Edge Function，前端呼叫端必須加入優雅靜默容錯，不得中斷主預約流程。

---

## 🏛️ 三、總結

Agent 5 已完成所有屬於維運、金流架構、環境變數與雲端規格之整改更新，專屬目錄 [`/infra/`](README.md) 下各項規範文件均已同步更新完備！
