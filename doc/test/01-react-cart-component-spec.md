---
description: React 購物車元件規格與測試案例清單（對標 deancourse/vibe-coding-testing-practice）
---

> 狀態：初始為 [ ]、完成為 [x]
> 注意：狀態只能在 Vitest / 測試全數通過驗收後由流程更新。
> 測試類型：前端元素、function 邏輯、Mock API、驗證權限、金流簽章、資安防護

---

## [ ] 【前端元素】購物車抽屜 (CartDrawer) 初始渲染與和色樣式
**範例輸入**：購物車狀態為空陣列 `items: []`  
**期待輸出**：畫面正確渲染日式和色抽屜面板，顯示「購物車目前是空的」，結帳按鈕處於 disabled 狀態。

---

## [ ] 【function 邏輯】商品加入與數量變更之響應式計算
**範例輸入**：加入「安定平衡複方 15ml」單價 1050 元 2 瓶，並加入「野橘 15ml」單價 500 元 1 瓶  
**期待輸出**：購物車總數量更新為 3，小計總額精確計算為 2600 元，觸發狀態變更但無副作用。

---

## [ ] 【資安防護】商品標題與顧客備註之 XSS 實體轉義
**範例輸入**：惡意注入字串 `<img src=x onerror=alert('xss')>` 作為備註  
**期待輸出**：React DOM 自動編碼輸出純文字字串，禁止執行任何非法腳本。

---

## [ ] 【Mock API】對接後端 /api/payments/create 金流建單合約 (MSW)
**範例輸入**：點擊「LINE Pay 結帳」，以 MSW 攔截 POST `/api/payments/create`  
**期待輸出**：帶出正確格式之 Payload（`items`, `total`, `order_id`），成功接收導向支付網址 `paymentUrl`。
