# 測試案例規格目錄 (`doc/test/`)

本目錄存放由 **🛡️ Agent 1（品管與測試工程師 · 第一順位品質守護）** 依據林鼎淵（Dean Lin）《Vibe Coding Testing Practice》自動化測試防禦規範所制訂的測試案例規格與驗收清單。

---

## 🏛️ 核心防呆五大工序 (Poka-Yoke Testing SOP)

1. **STEP 1 先規格後程式（Test-First Spec）**：建立 `doc/test/`，撰寫 Markdown 格式測試案例（【測試類型】測試說明、範例輸入、期待輸出），經 Review 確認邊界後才允許撰寫測試程式。
2. **STEP 2 測試結構嚴格對齊**：測試程式第二層 `describe()` 必須為「測試類型」，每個測試案例直接採用 Markdown 原文描述，不任意轉譯或改名。
3. **STEP 3 執行全量驗證與打勾標記**：執行全站 12 大深度測試矩陣（`python tests/run_all_tests.py`，100% 綠燈）；測試成功後將 `doc/test/` 之狀態由 `[ ]` 更新為 `[x]`。
4. **STEP 4 防回歸自我修復迴圈（Anti-Regression）**：若測試紅燈未符預期，最多重複修復 5 次，仍失敗則強制中斷並報告原因，杜絕 AI「越改越爛、按下葫蘆浮起瓢」。
5. **STEP 5 品質門神與分支保護（Branch Protection）**：全站資安掃描（XSS / 金流防刷 / 雙寫持久化）、API 整合端點測試、精油母體稽核。未通過 CI 綠燈嚴禁合入 `main` 正式分支。

---

## 📊 12 大測試案例規格對照表

| 階層 | 規格文件 (`doc/test/`) | 實作測試程式 (`tests/`) | 檢驗核心與邊界 | 負責 Agent |
| :---: | :--- | :--- | :--- | :---: |
| **L3** | [`api_endpoints.md`](file:///d:/01_Project/GitHub/doterra/doc/test/api_endpoints.md) | `tests/test_api_endpoints.py` | 後端 API 結構、IP 優先權、LINE Webhook 防回音死循環 | Agent 2 |
| **L3** | [`payment_api.md`](file:///d:/01_Project/GitHub/doterra/doc/test/payment_api.md) | `tests/test_payment_api.py` | LINE Pay v3 測試沙盒、防偽強制重算、HMAC 簽章與冪等 | Agent 5 / 2 |
| **L3** | [`security_audit.md`](file:///d:/01_Project/GitHub/doterra/doc/test/security_audit.md) | `tests/test_security_audit.py` | 全站照妖鏡：XSS 實體轉義、自然醫學法規、雙寫持久化 | Agent 1 照妖鏡 |
| **L3** | [`experience_handoff.md`](file:///d:/01_Project/GitHub/doterra/doc/test/experience_handoff.md) | `tests/test_experience_handoff.py` | 短效 600s Token 防刷加密、雙入口抽卡狀態機 | Agent 2 |
| **L2** | [`catalog_integrity.md`](file:///d:/01_Project/GitHub/doterra/doc/test/catalog_integrity.md) | `tests/test_catalog_integrity.py` | 精油母體規格、正整數零售價、容量標準與法規合規 | Agent 4 |
| **L2** | [`catalog_sync.md`](file:///d:/01_Project/GitHub/doterra/doc/test/catalog_sync.md) | `tests/test_catalog_sync.py` | 目錄同步腳本冪等性、CSV ↔ JSON 1:1 映射與位格歸屬 | Agent 4 |
| **L4** | [`asset_integrity.md`](file:///d:/01_Project/GitHub/doterra/doc/test/asset_integrity.md) | `tests/test_asset_integrity.py` | 全站靜態圖檔零破圖、HTML 本機資源零 404、購物車一致性 | Agent 3 |
| **L5** | [`live_endpoints.md`](file:///d:/01_Project/GitHub/doterra/doc/test/live_endpoints.md) | `tests/test_live_endpoints.py` | 正式環境 Render 後端、Vercel 8 頁面活體連線與延遲 | Agent 5 / 營運 |
| **L1** | [`js_syntax.md`](file:///d:/01_Project/GitHub/doterra/doc/test/js_syntax.md) | `tests/test_js_syntax.js` | 全站 18 個 JavaScript 模組 Node.js AST 語法編譯掃描 | Agent 3 / 1 |
| **L4** | [`cart_logic.md`](file:///d:/01_Project/GitHub/doterra/doc/test/cart_logic.md) | `tests/test_cart_logic.js` | 購物車狀態管理單元測試、數量增減與 LocalStorage 存取 | Agent 3 |
| **L4** | [`cart_integration.md`](file:///d:/01_Project/GitHub/doterra/doc/test/cart_integration.md) | `tests/test_cart_integration.js` | 購物車與預約結帳合約整合、URL Query 序列化與多品項運算 | Agent 3 |
| **L3** | [`supabase_client.md`](file:///d:/01_Project/GitHub/doterra/doc/test/supabase_client.md) | `tests/test_supabase_client.js` | 前端 Supabase RPC 客戶端安全調用、受付編號與防刷防偽 | Agent 2 / 3 |

---

## 🛠️ 外部標準基準庫 (Reference Benchmark)
- **標準基準庫**：`gh repo clone deancourse/vibe-coding-testing-practice`
- **本機沙盒兼容路徑**：`D:/00_Sandbox/vibe-coding-testing-practice`
- **工作流定義**：`.agent/workflows/gen-test-cases.md`、`.agent/workflows/test/test-doc-template.md`
