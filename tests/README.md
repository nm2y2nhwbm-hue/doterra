# 🧪 Agent 3：測試與品質檢驗目錄 (`/tests/`)

本目錄為 **Agent 3（測試助理專屬）** 唯一管轄維護範圍，掌管全站自動化測試、API 整合校驗、單元測試、E2E 端到端活體探測與 CI/CD 自動化建置。

---

## 📌 Agent 3 核心職責與測試矩陣

### 1. 後端 API 與安全防禦測試 (針對 Agent 1)
* **`tests/test_api_endpoints.py`**：檢驗 `/health`, `/api/oils`, `/api/indicators` 狀態碼與 JSON 回傳結構。
* **`tests/test_experience_handoff.py`**：檢驗短效防偽交接 Token 加密、有效期限與防竄改防刷機制。
* **`tests/test_catalog_integrity.py`**：檢驗 `doterra.csv` 與 `static/oils-catalog.json` 資料庫完整性、SKU 格式、建議零售價為正整數、容量規格（15ml / 5ml / 10ml / 115ml）、三大位格標記以及 100% 排除醫療法規高風險用詞（全面遵循「自然醫學」標準）。

### 2. 前端元件與狀態邏輯測試 (針對 Agent 2)
* **`tests/test_cart_logic.js`**：檢驗 Agent 2 購物車模組（`components/cart/cart.js`）加入商品、數量增減（增至上限／減至 0 自動移除）、單筆移除、全單清空、LocalStorage 持久化存取與總金額精準加乘計算。
* **`tests/test_supabase_client.js`**：檢驗前端與 Supabase RPC 串接、匿名防護與預約建立呼叫。
* **`tests/test_asset_integrity.py`**：檢驗全站靜態資源完整性、69 款精油與 12 款指示卡實體圖檔 100% 存在、HTML 資源參照零 404 破圖、購物車元件與靜態發布目錄同步率、以及全站 8 大核心頁面 SEO 與 GA4 標籤。
* **`tests/test_js_syntax.js`**：以 Node.js 執行全站 13 個 JavaScript 模組的靜態編譯與語法安全性檢測。

### 3. 線上正式環境端點活體探測與品質監測
* **`tests/test_live_endpoints.py`**：
  * 探測 Render 生產端點（`https://doterra-73pv.onrender.com`）：`/health`、`/api/oils`、`/api/indicators`、CORS 跨域標頭與回應延遲。
  * 探測 Vercel 生產端點（`https://doterra-two.vercel.app`）：8 大前台與後台頁面 HTTP 200 存活狀態、購物車資產（`cart.css`、`cart.js`）以及 CDN 快取標頭。

### 4. CI/CD 自動化管線 (`.github/workflows/ci.yml`)
* 每次推送（`push`）或發起合併請求（`pull_request`）至 `main` 時，自動於 GitHub Actions 虛擬機啟動：
  * **Python 3.12 測試作業**：安裝依賴並全量執行單元測試、資料庫合規測試、資產破圖檢測與正式端點探測。
  * **Node.js 20 測試作業**：執行全量 JavaScript 靜態編譯檢驗、Supabase 客戶端測試與購物車邏輯測試。

---

## 🚀 本地測試執行指令

```bash
# 1. 執行全量 Python 測試套件 (含 API、交接 Token、資料完整性、零破圖、正式端點)
python -m unittest discover tests

# 2. 執行個別 Python 測試模組
python -m unittest tests/test_api_endpoints.py
python -m unittest tests/test_experience_handoff.py
python -m unittest tests/test_catalog_integrity.py
python -m unittest tests/test_asset_integrity.py
python -m unittest tests/test_live_endpoints.py

# 3. 執行 Node.js 前端元件與語法測試
node tests/test_supabase_client.js
node tests/test_cart_logic.js
node tests/test_js_syntax.js
```