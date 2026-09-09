# 🌐 品牌自訂頂級網域綁定與 DNS 設定指南

本文件提供將自購品牌獨立網域（例如 `yourdomain.com`）對接至 Vercel 前端與 Render 後端的完整 DNS 記錄配置標準。

---

## 🛠️ 架構規劃

```
                     DNS 託管商 (Cloudflare / GoDaddy / 智邦)
                                 │
         ┌───────────────────────┴───────────────────────┐
         │                                               │
   A / CNAME 記錄                                   CNAME 記錄
         │                                               │
         ▼                                               ▼
┌─────────────────┐                             ┌─────────────────┐
│  Vercel Edge    │                             │   Render API    │
│  前端靜態服務   │                             │   後端伺服器    │
│  (yourbrand.tw) │                             │(api.yourbrand.tw│
└─────────────────┘                             └─────────────────┘
```

---

## 📋 DNS 記錄配置表

在您的網域名稱註冊商（如 Cloudflare、GoDaddy、Gandi 等）控制台新增下列記錄：

### 1. 前端官網（Vercel）
| 類型 | 主機名稱 (Name) | 內容 (Target / Value) | 代理狀態 (Proxy) | 說明 |
| :--- | :--- | :--- | :---: | :--- |
| **A** | `@`（根網域） | `76.76.21.21` | DNS Only / Proxied | 指向 Vercel Anycast IP |
| **CNAME** | `www` | `cname.vercel-dns.com` | DNS Only / Proxied | 指向 Vercel 邊緣節點 |

### 2. 後端 API 服務（Render）
| 類型 | 主機名稱 (Name) | 內容 (Target / Value) | 代理狀態 (Proxy) | 說明 |
| :--- | :--- | :--- | :---: | :--- |
| **CNAME** | `api` | `doterra-73pv.onrender.com` | DNS Only | 指向 Render 伺服器 |

---

## 🔒 憑證與安全性注意事項

1. **自動 SSL 憑證**：
   * Vercel 與 Render 均提供免費的 Let's Encrypt 自動 SSL 憑證簽發。
   * DNS 記錄生效後約 5~15 分鐘即可完成 HTTPS 驗證。
2. **CORS 與環境變數更新**：
   * 當切換至自訂網域時，需通知 **Agent 1** 更新 [`line_bot.py`](../line_bot.py) 的 CORS 白名單，將新網域加入信任清單。
   * 更新 LINE Developer Console 中的 Webhook URL 與 LIFF Endpoint URL。
