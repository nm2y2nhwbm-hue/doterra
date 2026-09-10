# 🧪 Agent 3：自動化測試與品質檢驗深度架構 (`/tests/`)

本目錄為 **Agent 3（品管與測試工程師專屬）** 唯一管轄維護範圍，掌管全站自動化測試矩陣、API 整合校驗、單元測試、E2E 結帳整合、日式美學規範稽核、正式端點活體探測與 CI/CD 自動化建置。

---

## 🏛️ 六大深度檢驗階層架構 (Testing Depth 2.0 Pyramid)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ Agent 3 自動化測試深度階梯架構（Depth Pyramid 2.0）                           │
├───────────────────────────────────────────────────────────────────────────────┤
│ L6 統一調度層 │ run_all_tests.py + GitHub Actions CI/CD 管線矩陣              │
│ L5 線上韌性層 │ test_live_endpoints.py (延遲閾值、CDN 快取、SSL/HTTPS 活體)   │
│ L4 前端美學層 │ test_asset_integrity.py + test_cart_logic.js +                │
│               │ test_cart_integration.js (日式美學、蒔繪金箔、結帳資料合約)  │
│ L3 後端安全層 │ test_api_endpoints.py + test_experience_handoff.py +          │
│               │ test_payment_api.py + test_supabase_client.js                 │
│               │ (7 大 API 路由、IP 防偽、金流驗簽、短效 Token 邊界)           │
│ L2 資料同步層 │ test_catalog_sync.py + test_catalog_integrity.py              │
│               │ (Agent 4 CSV↔JSON 1:1 精確同步、建議零售價與官方容量校驗)     │
│ L1 語法安全層 │ test_js_syntax.js (全站 JS AST 語法編譯解析、零保留字污染)    │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 📌 完整測試套件矩陣清單

### 1. L3 & L5 後端 API、第三方金流與安全防禦 (針對 Agent 1 / Agent 5)
* **`tests/test_api_endpoints.py`**：檢驗 `/health`、`/api/oils`、`/api/indicators`、`/api/draws/health`、`/api/draws`、`/api/draws/redeem`、`/api/log-draw` 狀態碼與 JSON 結構、反向代理多重 IP 辨識安全，以及 LINE Webhook 抽卡結果防回音死循環攔截（`test_line_webhook_echo_loop_prevention`）。
* **`tests/test_payment_api.py`**：檢驗第三方金流（綠界 ECPay / LINE Pay）建立、金額防偽強制重算、CheckMacValue 簽章演算法、異步 Webhook 驗證與冪等性防護。
* **`tests/test_experience_handoff.py`**：檢驗短效防偽交接 Token 加密、有效期限（600s）與防竄改防刷機制。
* **`tests/test_security_audit.py`**：**[全新照妖鏡防線]** 檢驗全站 Stored/DOM XSS 實體轉義（`static/inventory.js`、`components/cart/cart.js`、`static/booking.js`、`static/admin.js`）、`core/keep_warm.py` 外部 Ingress 保溫探針、`core/payment_manager.py` 訂單 Supabase PostgreSQL 雙寫持久化與冷啟動檢索恢復，以及衛福部自然醫學零違規詞彙強制斷言。
* **`tests/test_live_endpoints.py`**：實體探測 Render 生產 API、Vercel 8 大頁面、購物車資產、CDN 快取與回應延遲閾值。

### 2. L2 商品目錄與定價同步校驗 (針對 Agent 4)
* **`tests/test_catalog_sync.py`**：檢驗 Agent 4 `catalog/sync_catalog.py` 執行邏輯與冪等性，驗證 `doterra.csv` 與 `static/oils-catalog.json` 每一筆精油之建議零售價、官方容量與三大位格（中柱/左柱/右柱）1:1 精準映射。
* **`tests/test_catalog_integrity.py`**：檢驗資料庫完整性、SKU 格式、建議零售價為正整數、容量規格（15ml / 5ml / 10ml / 115ml）以及 100% 排除醫療法規高風險用詞（全面遵循「自然醫學」標準）。

### 3. L1 & L4 前端元件、購物車與日式款待美學 (針對 Agent 2)
* **`tests/test_cart_logic.js`**：檢驗購物車模組（`components/cart/cart.js`）加入商品、數量增減、單筆移除、全單清空、LocalStorage 持久化存取與總金額精準加乘。
* **`tests/test_cart_integration.js`**：檢驗購物車與 `booking.html` 預約結帳資料合約整合、URL 查詢參數編碼與多品項加權金額精度。
* **`tests/test_supabase_client.js`**：檢驗前端與 Supabase RPC 串接、匿名防護與預約建立呼叫。
* **`tests/test_asset_integrity.py`**：檢驗全站 69 款精油與 12 款指示卡實體圖檔 100% 存在、HTML 資源參照零 404 破圖、購物車元件與靜態發布目錄同步率、CSS 內部 `url()` 字型與圖檔 100% 存在、日式款待美學核心規範（LINE Seed TW、蒔繪金箔細線 `#b8912e`、`--shadow-diffuse`、呼吸感行高、平滑過渡）、首頁選品卡片 `data-cart-item` 規格合法性、以及全站 8 大核心頁面 SEO 與 GA4 標籤。
* **`tests/test_js_syntax.js`**：以 Node.js 遞迴掃描全站（`static/`、`components/`、`tests/`）全量 18 個 JavaScript 模組的靜態編譯與 AST 語法安全性檢測。

### 4. L6 自動化調度與 CI/CD 管線
* **`tests/run_all_tests.py`**：Agent 3 專屬一鍵執行全量測試調度器，自動偵測 Python 與 Node.js 環境，輸出結構化報表與耗時分析（12 大套件秒級全綠通過）。
* **`.github/workflows/ci.yml`**：每次推送或 PR 時自動於 GitHub Actions 啟動 Python 3.12 與 Node.js 20 雙環境自動化測試管線。


---

## 🚀 測試執行指令

### 一鍵執行全量深度測試 (推薦)
```bash
python tests/run_all_tests.py
```

### 個別測試模組執行
```bash
# 1. 執行全量 Python 測試套件
python -m unittest discover tests

# 2. 執行個別 Python 測試
python -m unittest tests/test_api_endpoints.py
python -m unittest tests/test_payment_api.py
python -m unittest tests/test_experience_handoff.py
python -m unittest tests/test_catalog_integrity.py
python -m unittest tests/test_catalog_sync.py
python -m unittest tests/test_asset_integrity.py
python -m unittest tests/test_live_endpoints.py

# 3. 執行 Node.js 前端元件與語法測試
node tests/test_js_syntax.js
node tests/test_cart_logic.js
node tests/test_cart_integration.js
node tests/test_supabase_client.js
```

---

## 📋 跨 Agent 品質稽核發現與協同備忘 (Cross-Agent Memos)

品管檢驗所發現之跨領域優化建議（如日式和色 Token 整併、動態留白「間」、微互動「殘心」與款待文案建議），完整登載於：
👉 **[`tests/QA_COLLABORATION_MEMO.md`](./QA_COLLABORATION_MEMO.md)**

供 **Agent 1（後端）**、**Agent 2（前端）**、**Agent 4（文案）**、**Agent 5（維運）** 隨時查閱並作為下一輪迭代之具體優化指引。