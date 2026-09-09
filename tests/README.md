# 🧪 Agent 3：測試與品質檢驗目錄 (`/tests/`)

本目錄為 **Agent 3** 專屬維護範圍，掌管所有自動化測試、API 整合校驗、單元測試、E2E 端到端走查與 CI 驗證。

---

## 📌 負責職責
1. **後端 API 測試 (針對 Agent 1)**：
   * `test_api_endpoints.py`：檢驗 `/health`, `/api/oils`, `/api/indicators`, `/api/draws` 狀態碼與 JSON 欄位結構。
   * `test_experience_handoff.py`：檢驗短效防偽 Token 加密、有效期限與防竄改機制。
2. **前端元件與 UI 測試 (針對 Agent 2)**：
   * `test_supabase_client.js`：檢驗前端與 Supabase RPC 串接。
   * 檢驗購物車 LocalStorage 讀寫、數量加減與總金額計算邏輯。
   * 驗證網頁無 404 破圖、無 Console 腳本報錯。
3. **品質稽核與門檻**：
   * 執行全站資安、PageSpeed 效能與自然醫學法規合規性複查。

---

## 🚀 測試執行指令
```bash
# 執行 Python 後端與 API 測試
python -m unittest discover tests

# 執行個別測試腳本
python tests/test_experience_handoff.py
```