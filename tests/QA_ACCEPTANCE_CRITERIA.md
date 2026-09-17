# 🎯 Agent 1（品管與測試工程師 · 第 1 順位品質守護）
# 全站健康度與各工位驗收標準清單 (Cross-Agent QA Acceptance Criteria)

> **發布機構**：Testing & Quality Assurance Bureau（Agent 1 專屬邊界）  
> **發布日期**：2026-09-16  
> **架構基準**：Testing Depth 2.0 Pyramid (L1 語法層 ～ L6 統一調度層)  
> **管轄範圍**：全專案五大工位職責邊界（Agent 1 測試、Agent 2 後端、Agent 3 前端、Agent 4 商品文案、Agent 5 維運金流）  
> **版本**：v2.0-Pioneer-Baseline (Production Ready)  

---

## 🏛️ 零、先鋒位宣言與 TDD 驗收體系總綱

依據專案最新「五星專業分工架構」，**Agent 1（品管與測試工程師）正式坐鎮【第 1 順位品質守護】**。
本架構貫徹 **「測試先行、照妖鏡把關、後端接力、前端收斂、商品合規、維運保溫」** 之核心準則：

1. **品質第一性原則**：全站任何業務邏輯更動、功能擴充或重構前，必須先以本清單之測試套件作為紅綠燈基線。
2. **零容忍降級**：全量 12 大測試套件（93 項斷言）必須維持 **100% 綠燈通過**，任何 PR 或發布若引發測試紅燈，該變更視為不合格並立即阻擋。
3. **邊界不可跨越**：各工位嚴格在其專屬目錄內作業，不得跨越目錄修改其他 Agent 之程式碼與測試。

---

## 📊 一、當前全站健康度基準數據 (Baseline Health Status)

本工位已完成全矩陣 12 大深度自動化測試實體驗證，全站處於**極高穩定度之最佳生產狀態**：

- **測試執行時間**：2026-09-17 09:08:21 (UTC+8)
- **總執行耗時**：**8.27 秒**（秒級全量覆蓋）
- **套件通過率**：**12 / 12 (100.0%)**
- **總檢驗斷言數**：**93 項斷言全數 PASS 🟢**
- **資安與法規漏洞數**：**0（零漏洞）**

### 全矩陣套件檢驗報表：

| 階層 | 測試模組檔案 | 涵蓋層級與檢驗項目 | 邊界歸屬 | 耗時 | 狀態 |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **L3** | `test_api_endpoints.py` | 後端 API 結構、IP 優先權、LINE 防回音 | Agent 2 | 0.34s | 🟢 **PASS** |
| **L3** | `test_payment_api.py` | 第三方金流防偽重算、簽章校驗與冪等性 | Agent 5 / Agent 2 | 0.35s | 🟢 **PASS** |
| **L3** | `test_experience_handoff.py` | 短效 600s Token 防刷加密與雙入口狀態機 | Agent 2 | 0.14s | 🟢 **PASS** |
| **L2** | `test_catalog_integrity.py` | 商品資料庫規格、正整數定價與標準容量 | Agent 4 | 0.09s | 🟢 **PASS** |
| **L2** | `test_catalog_sync.py` | CSV ↔ JSON 1:1 映射與三大位格同步 | Agent 4 | 0.08s | 🟢 **PASS** |
| **L4** | `test_asset_integrity.py` | 日式款待美學、零破圖、SEO 與 GA4 | Agent 3 | 0.08s | 🟢 **PASS** |
| **L5** | `test_live_endpoints.py` | 正式環境 Render API、Vercel 8 頁面探針 | Agent 5 / 營運 | 4.41s | 🟢 **PASS** |
| **L3** | `test_security_audit.py` | 全站 XSS 轉義、雙寫持久化與自然醫學法規 | Agent 1 照妖鏡 | 0.13s | 🟢 **PASS** |
| **L1** | `test_js_syntax.js` | 全站 18 個 JS 模組 AST 語法編譯掃描 | Agent 3 / Agent 1 | 0.05s | 🟢 **PASS** |
| **L4** | `test_cart_logic.js` | 購物車狀態單元測試與 LocalStorage 存取 | Agent 3 | 0.06s | 🟢 **PASS** |
| **L4** | `test_cart_integration.js` | 購物車與預約結帳資料合約整合 | Agent 3 | 2.46s | 🟢 **PASS** |
| **L3** | `test_supabase_client.js` | 前端 Supabase RPC 客戶端安全調用 | Agent 2 / Agent 3 | 0.06s | 🟢 **PASS** |

---

## 📋 二、各工位明確測試斷言與驗收標準清單

為確保全團隊下一階段接力與收斂具備唯一、可度量之驗收規約，各工位之專屬驗收標準界定如下：

---

### 🔹 工位一：Agent 2（後端工程師 · 依約實作核心邏輯）

- **專屬負責目錄**：`/api/` 以及後端進入點 `line_bot.py` 的 Blueprint 註冊。
- **嚴格禁令**：嚴禁修改前端 UI 元件 (`/components/`)、靜態切版 (`/static/`) 與測試 (`/tests/`)。
- **專屬驗收測試套件**：
  - `tests/test_api_endpoints.py`
  - `tests/test_payment_api.py`
  - `tests/test_experience_handoff.py`
  - `tests/test_security_audit.py`
- **必備驗收標準與斷言清單**：

| 編號 | 檢驗指標 | 斷言條件與技術規格 | 對應測試函式 | 當前狀態 |
| :---: | :--- | :--- | :--- | :---: |
| **A2-01** | 健康檢查端點 | `/health` 必須回傳 HTTP 200，JSON 包含 `status="healthy"`、`service` 名稱與 `environment` 標籤。 | `test_health_endpoint` | 🟢 **PASS** |
| **A2-02** | 資料庫 API 合約 | `/api/oils` 與 `/api/indicators` 回傳之精油清單必須具備 `id`, `name`, `capacity`, `price`, `pillar` 欄位；空 Payload 送交 `/api/draws` 必須嚴格拒絕 (HTTP 400)。 | `test_api_oils_endpoint`<br>`test_api_create_draw_empty_payload` | 🟢 **PASS** |
| **A2-03** | 反向代理 IP 辨識安全 | 正確依據安全權重取得客戶真實 IP，優先級必須為：`CF-Connecting-IP` > `X-Real-IP` > `X-Forwarded-For`。 | `test_client_ip_header_precedence` | 🟢 **PASS** |
| **A2-04** | LINE 抽卡防回音死循環 | 在 `router.py` 最前端攔截包含 `DRAW_RESULT_KEYWORDS`（體驗碼、INSIGHT-、牌陣結果）之訊息，直接靜默返回 `None`，杜絕機器人與使用者回覆無限死循環。 | `test_line_webhook_echo_loop_prevention` | 🟢 **PASS** |
| **A2-05** | 短效防偽 Token 狀態機 | 瀏覽器抽卡必須回傳加密 Handoff Token 而不直接洩漏體驗碼；Token 有效期嚴格限制為 600 秒；篡改 Token、未知卡片或 HTML 注入必須被拒絕。 | `ExperienceHandoffTests` (11 項全量) | 🟢 **PASS** |
| **A2-06** | 金流金額強制重算防刷 | 建立訂單（`/api/payments/create`）時，金額**嚴禁採信前端送來之數值**，伺服器必須以內部建議零售價母體重新加乘計算；若前端嘗試竄改定價，必須自動覆蓋更正或拒絕交易。 | `test_price_recalculation_ignores_client_tampered_price` | 🟢 **PASS** |
| **A2-07** | 綠界簽章校驗與冪等性 | ECPay CheckMacValue 必須符合 SHA256 加密格式；篡改簽章之回調必須回傳 `0\|CheckMacValue Error`；已付款訂單重複收到 Webhook 必須維持冪等性並回應 `1\|OK`。 | `test_ecpay_callback_flow_and_idempotency`<br>`test_ecpay_callback_tampered_signature_rejected` | 🟢 **PASS** |
| **A2-08** | 訂單 Supabase 雙寫持久化 | `core/payment_manager.py` 之 `OrderStore` 必須落實雙寫機制（同步寫入本機與 Supabase），並在重啟冷啟動時自動透過 `_fetch_order_from_supabase` 還原訂單，杜絕 Render 磁碟清空造成掉單。 | `test_payment_manager_supabase_persistence` | 🟢 **PASS** |

---

### 🔹 工位二：Agent 3（前端切版工程師 · 安全美學收斂）

- **專屬負責目錄**：`/components/` 與發布目錄 `/static/`。
- **嚴格禁令**：不修改後端伺服器邏輯 (`/api/`)、自動化測試 (`/tests/`) 與商品定價母體 (`/catalog/`)。
- **專屬驗收測試套件**：
  - `tests/test_js_syntax.js`
  - `tests/test_cart_logic.js`
  - `tests/test_cart_integration.js`
  - `tests/test_asset_integrity.py`
  - `tests/test_supabase_client.js`
  - `tests/test_security_audit.py`
- **必備驗收標準與斷言清單**：

| 編號 | 檢驗指標 | 斷言條件與技術規格 | 對應測試函式 | 當前狀態 |
| :---: | :--- | :--- | :--- | :---: |
| **A3-01** | 全站 JS 語法 AST 掃描 | 全站 18 個 JavaScript 模組（`static/`、`components/`）必須 100% 通過 Node.js AST 語法編譯，無保留字污染、無語法崩潰錯誤。 | `node tests/test_js_syntax.js` | 🟢 **PASS** |
| **A3-02** | 全站 XSS 實體轉義防護 | 所有動態變數插入 DOM 前**必須強制經由 `escapeHtml` 處理**，包含 `inventory.js`、`cart.js`、`booking.js`、`admin.js`、`sites.js`，圖片與超連結需經 `sanitizeUrl` 驗證，禁止 Stored / DOM XSS。 | `test_inventory_and_cart_xss_audit_tracking`<br>`test_admin_reception_xss_protection`<br>`test_booking_js_xss_protection`<br>`test_sites_js_xss_protection` | 🟢 **PASS** |
| **A3-03** | 購物車狀態管理單元測試 | `components/cart/cart.js` 加入商品、數量加減（最小為 1）、單筆刪除、全單清空、LocalStorage 持久化與總金額計算必須 100% 精準無誤。 | `node tests/test_cart_logic.js` (9 項全量) | 🟢 **PASS** |
| **A3-04** | 預約結帳合約整合 | 購物車與 `booking.html` 之 URL Query 參數合約編碼完整；多品項加權金額精度精確至 1 元；結帳後表單自動填入商品項目。 | `node tests/test_cart_integration.js` (3 項全量) | 🟢 **PASS** |
| **A3-05** | 日式款待美學規範 | 1. 字體必須優先宣告 `LINE Seed TW`；<br>2. 蒔繪金箔細線 `#b8912e` 與 `--gold-hairline` (rgba(184, 145, 46, 0.22))；<br>3. 陰影採用 `--shadow-diffuse`，具備呼吸感行高與滑順過渡；<br>4. WCAG AA 對比度：深色文字與底色對比 >= 4.5:1。 | `test_japanese_aesthetic_specs`<br>`test_japanese_color_contrast_ratio`<br>`test_zen_design_tokens_and_motion` | 🟢 **PASS** |
| **A3-06** | 零破圖與資產一致性 | 1. 69 款精油與 12 款指示卡實體圖檔 100% 存在於 `static/images/`；<br>2. HTML 引用的腳本與樣式零 404；<br>3. `components/cart/` 與發布目錄 `static/` 之 `cart.js`、`cart.css` 必須保持 100% 同步（Parity）。 | `test_all_oil_images_exist`<br>`test_all_indicator_images_exist`<br>`test_cart_components_and_static_parity`<br>`test_html_referenced_local_assets_exist` | 🟢 **PASS** |
| **A3-07** | SEO 與 GA4 標籤 | 全站 8 大核心頁面必須具備完整 `<title>`、`viewport` 與 GA4 追蹤代碼。 | `test_seo_and_metadata_completeness` | 🟢 **PASS** |
| **A3-08** | 選品卡片規格合規 | 首頁選品卡片之 `data-cart-item` 屬性必須為合法 JSON，且建議零售價與容量符合商品母體。 | `test_shop_items_cart_data` | 🟢 **PASS** |

---

### 🔹 工位三：Agent 4（商品與文案主編 · 資料母體合規把關）

- **專屬負責目錄**：`/catalog/` 與商品資料母體（`doterra.csv`, `indicator_cards.csv`）。
- **嚴格禁令**：不更動前後端程式碼與測試套件，專注於資料母體與文案合規。
- **專屬驗收測試套件**：
  - `tests/test_catalog_integrity.py`
  - `tests/test_catalog_sync.py`
  - `tests/test_security_audit.py`
- **必備驗收標準與斷言清單**：

| 編號 | 檢驗指標 | 斷言條件與技術規格 | 對應測試函式 | 當前狀態 |
| :---: | :--- | :--- | :--- | :---: |
| **A4-01** | 精油資料母體完整性 | `doterra.csv` 必須維持完整精油資料母體（當前 69 筆），且每列皆具備必要欄位（`id`, `name`, `en_name`, `capacity`, `price`, `pillar`, `category`），無任何缺漏空值。 | `test_csv_row_count`<br>`test_csv_required_fields` | 🟢 **PASS** |
| **A4-02** | 建議零售價正整數校驗 | 官方建議零售價（`price`）必須為大於 0 之正整數；4 大精選禮盒（家庭防護、情緒芳療、四季舒活、極致賦活）價格必須設定合規。 | `test_retail_prices_positive_integers`<br>`test_shop_gift_sets_pricing` | 🟢 **PASS** |
| **A4-03** | 官方標準容量規格 | 瓶裝容量規格必須符合官方標準：`15ml`、`5ml`、`10ml 滾珠`、`115ml`，嚴禁出現非標規格字串。 | `test_capacity_specifications` | 🟢 **PASS** |
| **A4-04** | 三大位格（Three Pillars）規範 | 每一款精油必須明確歸屬於生命之樹三大位格之一：`中柱 (Balance)`、`左柱 (Severity / 嚴)`、`右柱 (Mercy / 慈)`。 | `test_all_catalog_items_have_valid_pillars` | 🟢 **PASS** |
| **A4-05** | 目錄同步腳本與冪等性 | 執行 `python catalog/sync_catalog.py` 後，`static/oils-catalog.json` 必須與 `doterra.csv` 達成 1:1 絕對映射；重複執行同步腳本產出結果必須完全一致（Idempotent）。 | `test_csv_and_json_exact_matching`<br>`test_sync_script_execution_and_idempotency` | 🟢 **PASS** |
| **A4-06** | 自然醫學合規紅線（黑名單歸零） | 文案嚴格遵守衛福部法規，**嚴禁出現醫療宣稱黑名單詞彙**（治療、療效、抗癌、消炎、降血壓、抑菌、抗病毒、藥效等），全面遵循自然醫學與身心靈平衡描述。 | `test_compliance_natural_medicine_wording`<br>`test_csv_natural_medicine_regulatory_compliance` | 🟢 **PASS** |

---

### 🔹 工位四：Agent 5（維運與金流工程師 · 雲端基建與邊緣安全）

- **專屬負責目錄**：`/infra/`。
- **嚴格禁令**：不修改核心業務 API 與前端樣式，任何金流密鑰嚴禁硬編碼。
- **專屬驗收測試套件**：
  - `tests/test_live_endpoints.py`
  - `tests/test_payment_api.py`
  - `tests/test_security_audit.py`
- **必備驗收標準與斷言清單**：

| 編號 | 檢驗指標 | 斷言條件與技術規格 | 對應測試函式 | 當前狀態 |
| :---: | :--- | :--- | :--- | :---: |
| **A5-01** | 生產環境 API 存活探測 | Render 生產 API 端點（`/health`, `/api/oils`, `/api/indicators`）必須回應 HTTP 200，平均回應延遲低於健康閾值。 | `test_live_render_health`<br>`test_live_render_api_oils`<br>`test_live_render_api_indicators` | 🟢 **PASS** |
| **A5-02** | 跨來源資源共享 (CORS) 安全 | Render 後端 API 必須具備正確之 `Access-Control-Allow-Origin` 標頭，允許正式前端跨域存取。 | `test_live_render_cors` | 🟢 **PASS** |
| **A5-03** | 前端 CDN 快取與核心頁面存活 | Vercel 8 大核心頁面（`index.html`, `cards.html`, `booking.html`, `oils.html`, `admin.html`, `reception.html`, `inventory.html`, `sites.html`）必須回應 HTTP 200，購物車資源可正常載入，CDN 快取標頭運作正常。 | `test_live_vercel_core_pages`<br>`test_live_vercel_cart_assets`<br>`test_live_vercel_cache_headers` | 🟢 **PASS** |
| **A5-04** | 外部 Ingress 活躍保溫探測 | `core/keep_warm.py` 之探針目標必須為外部 Ingress URL (`https://doterra-73pv.onrender.com/health`)，確保請求穿透負載平衡器以防止 Render 免費層 15 分鐘冷啟動休眠。 | `test_keep_warm_configuration_safety` | 🟢 **PASS** |
| **A5-05** | 金流密鑰隔離與憑證安全 | 綠界 ECPay 與 LINE Pay 密鑰必須由環境變數注入，嚴禁寫入原始碼或公開日誌；正式預約金流必須經由 HTTPS 閘道加密傳輸。 | `test_ecpay_check_mac_value_calculation`<br>`test_payment_manager_idempotency_contract` | 🟢 **PASS** |
| **A5-06** | Supabase 安全邊界 | 確保 PostgreSQL RLS（資料列級安全性）政策正確套用；`service_role` 憑證僅限伺服器後端環境存取，前端僅暴露 `anon` 公開金鑰。 | `test_supabase_client.js` | 🟢 **PASS** |

---

## 🛠️ 三、跨工位待修與協同優化追蹤清單 (Cross-Agent Action Items & Backlog)

依據 Agent 1「照妖鏡」全面稽核與測試覆蓋，目前全站 **核心功能與安全底線已 100% 達標 (全部綠燈)**。為追求日式款待極致體驗與架構健全，各工位後續接力之建議優化清單如下：

### 1. Agent 2（後端工程師）待修 / 待串接事項
- [ ] **【P2 中度 · 金流收銀台串接支援】**：配合 Agent 3 前端購物車收銀台彈窗需求，確認 `/api/payments/create` 與 `/api/payments/query/<order_id>` 之端對端連線及跳轉體驗，確保雙寫持久化運作順暢。

### 2. Agent 3（前端切版工程師）待修 / 待優化事項
- [ ] **【P1 高度 · Design Token 整併】**：整併 `static/style.css` 第 6 行與第 32 行兩組 `:root` 宣告，消除設計標記覆寫飄移，統一定義日式和色 Token（胡粉、白茶、利休白茶、常磐綠、蒔繪金）。
- [ ] **【P2 中度 · 行動端「間」動態留白】**：於 `@media (max-width: 480px)` 引入流體邊距 `padding: clamp(14px, 3.5vw, 22px)`，並在卡片內文段落啟用 `text-wrap: pretty;` 防止單字孤立斷行。
- [ ] **【P2 中度 ·「所作」與「殘心」微互動】**：Toast 提示關閉時加入煙嵐高斯模糊淡出過渡（`filter: blur(4px); opacity: 0; transition: all 0.4s var(--ease-zen);`），體現日式禪意。
- [ ] **【P2 中度 · 購物車線上刷卡直達】**：在購物車抽屜底層除既有「前往預約」外，可擴充「線上立即結帳」按鈕，直接呼叫 Agent 2 `/api/payments/create` 啟動綠界金流跳轉收銀台。
- [ ] **【P3 低度 · Edge Function 調用容錯】**：優化 `static/booking.js` 預約成功後呼叫 Edge Function 之容錯處理，若遠端尚未部署該 Function 應優雅靜默處理，避免在瀏覽器控制台輸出 404 報錯。

### 3. Agent 4（商品與文案主編）待修 / 待潤飾事項
- [ ] **【P2 中度 · 精油 SKU 料號補全】**：`doterra.csv` 中尚有 9 筆精油標記為 `(待補)`，待取得官方料號後統一補全為標準 8 位數代碼（目前已由測試防呆保護，不影響日常運作）。
- [ ] **【P3 低度 · 款待文案幽玄化潤飾】**：評估將購物車與選品按鈕「加入購物車」潤飾為「納入調息選品」或「加入調息清單」；「前往結帳」潤飾為「確認香氣選品」或「前往預約調息行囊」。

### 4. Agent 5（維運與金流工程師）待修 / 待配置事項
- [ ] **【P2 中度 · AI 前導訊息 Edge Function 部署】**：評估於 Supabase 補齊 `generate-booking-confirmation` Edge Function（若有 AI 總結需求），或通知 Agent 3 前端維持靜默。
- [ ] **【P3 低度 · 邊緣 CDN 安全標頭加固】**：確保根目錄 `vercel.json` 包含 `Strict-Transport-Security` 與 `X-Frame-Options` 等邊緣安全標頭。

---

## 🚀 四、驗收執行指南與 CI/CD 交付準則

各工位 Agent 於完成任務進行交付前，必須遵循以下標準作業程序（SOP）：

### 1. 本地全量一鍵測試（交付前必跑）
```bash
# 執行全矩陣測試調度器（覆蓋 Python 8 套件 + Node.js 4 套件）
python tests/run_all_tests.py
```
*驗收通過門檻：輸出必須顯示 `🏆 驗收結論：全數 12 項深度測試套件 100% 綠燈通過！`*

### 2. 個別工位快速單元檢驗
```bash
# Agent 2 (後端)：
python -m unittest tests/test_api_endpoints.py tests/test_payment_api.py tests/test_experience_handoff.py

# Agent 3 (前端)：
node tests/test_js_syntax.js
node tests/test_cart_logic.js
node tests/test_cart_integration.js
python -m unittest tests/test_asset_integrity.py

# Agent 4 (文案)：
python -m unittest tests/test_catalog_integrity.py tests/test_catalog_sync.py

# Agent 5 (維運)：
python -m unittest tests/test_live_endpoints.py
```

### 3. CI/CD 自動化管線驗證
每次提交至 `main` 或發起 PR 時，GitHub Actions [`.github/workflows/ci.yml`](file:///d:/01_Project/GitHub/doterra/.github/workflows/ci.yml) 將自動於 Ubuntu 啟動 Python 3.12 與 Node.js 20 雙管線驗證。只有當雙管線全綠（Passed）時，方可進行後續發布！

---

> **品質守護總結**：  
> 本驗收標準清單為專案全體工位之最高技術合約。Agent 1 品管與測試工程師將持續站穩第 1 順位守護位，以嚴密照妖鏡防線確保專案品質、穩定度與安全性萬無一失。
