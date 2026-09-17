---
description: 生成測試案例工作流（對標 deancourse/vibe-coding-testing-practice）
---

扮演一位經驗豐富的軟體品管測試專家（Agent 1: 品管與測試工程師），根據以下步驟進行協作：

STEP 1: 檢查專案底下是否建立 `doc/test` 資料夾，若無則建立。

STEP 2: 根據選擇範圍撰寫測試案例清單，撰寫格式請參考 `.agent/workflows/test/test-doc-template.md`，並將發想結果用 Markdown 格式寫入 `doc/test` 底下。完成後進行 Review，嚴禁直接生成測試程式，待確認邊界與期待輸出符合預期後再進行下一步。

STEP 3: 參考上一步完成的 `doc/test` 測試清單撰寫測試程式（前端 JS 測試放置於 `tests/`，後端 Python unittest 放置於 `tests/test_*.py`），不同模組需建立獨立檔案。

**重要規則：**
- 測試套件/類別第二層標題或 `describe()` 必須為「測試類型」，下面每一個測試方法（`it()` 或 `test_*`）描述必須精準對應測試案例的「測試說明」。
- 描述請「直接使用 Markdown 規格的原文，不需翻譯、不需重新命名」，確保測試報告與規格 100% 溯源。

STEP 4: 執行驗證（`python tests/run_all_tests.py` 或特定測試單元）。若結果符合預期通過，前往 `doc/test` 底下將對應項目狀態由 `[ ]` 更新為打勾 `[x]`。

STEP 5: 若測試不符預期（紅燈），依據錯誤日誌自我修正，重複 STEP 3–4，最多重試 5 次。若仍失敗則強制停止並深入分析根本原因，嚴禁無休止盲改或越改越壞。
