# ☁️ Vercel 與 Render 雲端維運規格書 (`infra/cloud_specs.md`)

本文件由 **Agent 5（維運與金流工程師）** 制定，明確規範「現代精油心靈指引卡」專案之多雲部署架構、運算節點規格、快取策略與高可用性監控指引。

---

## 📐 一、多雲整體拓撲架構 (Multi-Cloud Topology)

```
                       使用者終端（Mobile Browser / LINE LIFF / Desktop）
                                              │
                     ┌────────────────────────┴────────────────────────┐
                     │                                                 │
          HTTPS 請求 (靜態資源 / UI)                           HTTPS API (動態運算 / Webhook)
                     │                                                 │
                     ▼                                                 ▼
        ┌─────────────────────────┐                       ┌─────────────────────────┐
        │       Vercel Edge       │                       │       Render API        │
        │      全球 Anycast CDN    │                       │     Python Web 服務     │
        │ (doterra-two.vercel.app)│                       │(doterra-73pv.onrender..)│
        └────────────┬────────────┘                       └────────────┬────────────┘
                     │                                                 │
                     │                 ┌───────────────────────────────┘
                     │                 │  Supabase Python Client / RPC
                     ▼                 ▼
        ┌───────────────────────────────────────────────────────────┐
        │                   Supabase Cloud (Tokyo)                  │
        │   - PostgreSQL 15 資料庫（RLS 隔離）                        │
        │   - Auth 身分鑑別服務（Admin 白名單）                       │
        │   - Edge Functions（庫存定時同步 sync-inventory）          │
        └───────────────────────────────────────────────────────────┘
```

---

## ⚡ 二、Vercel 前端邊緣規格 (Frontend Edge Specs)

### 1. 服務配置與區域
* **平台**：Vercel Production Platform
* **部署模式**：Static Site & Edge Network (零伺服器維護)
* **主節點區域**：`hnd1` (Tokyo, Japan) / Anycast 全球邊緣就近交付
* **生產網域**：`https://doterra-two.vercel.app`（支援自訂獨立頂級網域）
* **TLS / SSL**：Let's Encrypt 自動簽發、自動輪替，強制 TLS 1.3，啟用 HTTP/2 與 HTTP/3 (QUIC)

### 2. 快取政策 (Caching Policy)
* **HTML 靜態頁面**：`Cache-Control: public, max-age=0, must-revalidate`（確保發布時用戶即時載入最新版本）
* **JavaScript / CSS 資產**：`Cache-Control: public, max-age=31536000, immutable`（搭配版本雜湊或靜態長效快取）
* **圖片與多媒體 (`/static/images/`)**：`Cache-Control: public, max-age=86400, stale-while-revalidate=604800`（加速精油圖鑑圖檔載入）

### 3. 安全標頭規格 (Security Headers)
```http
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## 🐍 三、Render 後端容器規格 (Backend Web Service Specs)

### 1. 執行環境與實例規模
* **平台**：Render Cloud Web Service
* **環境類型**：Python 3.10+
* **進入點**：`gunicorn line_bot:app --workers 2 --threads 4 --timeout 120`
* **生產網域**：`https://doterra-73pv.onrender.com`（支援自訂子網域 `api.yourbrand.tw`）
* **資源配額**：
  - **CPU**：0.1 ~ 0.5 vCPU（可依尖峰平滑水平擴展）
  - **RAM**：512 MB
  - **連線逾時**：120 秒（滿足 LINE Webhook 異步處理與金流回調）

### 2. 健康檢查與保活策略 (Keep-Alive & Health Check)
* **健康端點**：`GET /health`
* **正常回應**：`HTTP 200 OK`，JSON: `{"status": "ok", "version": "2.1.0", "timestamp": ...}`
* **冷啟動 (Spin-Down) 防護方案**：
  - Render 免費方案於閒置 15 分鐘後會進入休眠（冷啟動需耗時 30~50 秒）。
  - **防護措施**：由外掛 UptimeRobot 或 GitHub Actions 定時每 10 分鐘發送一次 `GET /health`，保持容器處於常駐熱機（Warm）狀態，確保用戶結帳與抽卡零等待。

---

## 🗄️ 四、Supabase 維運規格 (Database & Auth Specs)

* **雲端主機區**：AWS `ap-northeast-1` (東京，Tokyo)
* **資料庫版本**：PostgreSQL 15 (Active Healthy)
* **連線安全**：
  - 強制 SSL 模式 (`sslmode=require`)
  - 嚴禁於瀏覽器客戶端暴露 `service_role` 密鑰
  - 核心資料表（`bookings`、`draws`、`orders`、`payment_logs`）強制啟用 RLS（Row Level Security）
* **維護日誌**：定時稽核連線數池（Pooler: PgBouncer）與磁碟容量配額。
