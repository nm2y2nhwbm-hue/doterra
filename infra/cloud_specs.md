# ☁️ Vercel 與 Render 雲端維運規格書 (`infra/cloud_specs.md`)

本文件由 **Agent 5（維運與金流工程師）** 制定，明確規範「現代精油心靈指引卡」專案之多雲部署架構、運算節點規格、快取策略、HSTS A+ 資安標頭與高可用性監控指引。

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

### 3. A+ 級安全標頭規格 (Security Headers & HSTS)
> 💡 依據 Agent 3 照妖鏡稽核建議（第 4.1 項），全站應具備防點擊劫持（Clickjacking）、MIME 嗅探與強制 HTTPS 傳輸之完整保護。

#### 標準配置範本 (`vercel.json` 邊緣路由注入標準)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=63072000; includeSubDomains; preload"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        },
        {
          "key": "Permissions-Policy",
          "value": "camera=(), microphone=(), geolocation=()"
        }
      ]
    }
  ]
}
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

### 2. 健康檢查與外部保活防護 (Keep-Alive & Ingress Awakening)
> 🚨 響應 Agent 3 照妖鏡通報（第 0.4 項）：Render 平台休眠偵測**僅採計經由外部 Ingress 負載平衡器之進站請求**；本機探測 `127.0.0.1` 無法被判定為活躍流量！

* **健康端點**：`GET /health`
* **正常回應**：`HTTP 200 OK`，JSON: `{"status": "ok", "version": "2.1.0", "timestamp": ...}`
* **雙軌外部保活架構 (Dual External Keep-Alive)**：
  1. **容器內外網喚醒配置**：
     - 後端服務環境變數必須注入 `KEEP_WARM_TARGET_URL=https://doterra-73pv.onrender.com/health`。
     - 容器內部保溫線程（`core/keep_warm.py`）探測時必須對該外部公開 HTTPS 網址發送請求，確保流量穿越 Render 外部 Ingress。
  2. **外部雲端排程防護 (UptimeRobot / Cron)**：
     - 在第三方免費監測平台（如 UptimeRobot 或 GitHub Actions 定時 Workflow）配置監控探針。
     - 設定頻率：**每 9 分鐘一次**（Render 休眠閥值為 15 分鐘）。
     - 探測目標：`https://doterra-73pv.onrender.com/health`。
     - 效益：徹底根絕容器冷啟動（Spin-Down），使結帳與 Webhook 響應時間維持在 **< 300ms**。

---

## 🗄️ 四、Supabase 維運規格 (Database & Functions Specs)

* **雲端主機區**：AWS `ap-northeast-1` (東京，Tokyo)
* **資料庫版本**：PostgreSQL 15 (Active Healthy)
* **連線安全**：
  - 強制 SSL 模式 (`sslmode=require`)
  - 嚴禁於瀏覽器客戶端暴露 `service_role` 密鑰
  - 核心資料表（`bookings`、`draws`、`orders`、`payment_logs`）強制啟用 RLS（Row Level Security）
* **Edge Functions 維運標準 (響應 Agent 3 第 0.6 項通報)**：
  - **已正式投產**：`sync-inventory`（定時庫存安全同步）。
  - **規劃中或未投產函式**（如 `generate-booking-confirmation`）：在 Edge Function 未由維運完成部署前，規範前端呼叫端必須加入 `try...catch` 靜默容錯，不可導致瀏覽器 Console 出現阻斷性 404 報錯。
