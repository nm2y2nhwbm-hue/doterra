# 現代精油庫存管理 iOS 捷徑流程與架構手冊 (v4.0.3)

本文件完整紀錄「精油庫存管理」iOS 捷徑之主選單架構、分支邏輯及 Google Apps Script (GAS) API 呼叫參數對應。

---

## 一、 主選單架構 (Main Menu)

捷徑啟動後，首先透過「從包含 `執行` 的選單中選擇」分為兩大主功能：
1. **執行庫存**
2. **查看精油庫存**[cite: 9]

---

## 二、 執行庫存模組

當選擇「執行庫存」時，提供以下三種動態作業選單：

### 1. 新增 (Add)
* **步驟說明**：
  1. 透過條碼掃描要求輸入文字[cite: 9]。
  2. 從要求輸入取得文字，以自訂 `|` 分隔文字並取得第一項[cite: 9]。
  3. 將該項目設為變數 `Barcode`[cite: 9]。
  4. **API 查詢**：呼叫 `GAS ?action=lookupProduct&barcode=Barcode`[cite: 9]。
  5. 從 URL 內容取得字典，讀取 `capacity`、`productName`、`status`[cite: 9]。
  6. **條件判斷 (`status` 是否為 `success`)**：
     * **[若成功 (Existing Product)]**：
       * 設定變數 `ProductName` 與 `capacity`[cite: 9]。
       * 透過 `ProductName` 要求輸入備註 (`Notes`)[cite: 9]。
       * 透過日期要求輸入選擇日期類型（`MFG` 製造日 或 `EXP` 有效日）[cite: 9, 13]。
       * 若選擇 `MFG`：將要求輸入加上 5 年，並格式化為調整後的有效日期 (`ExpiryDate`)[cite: 13]。
       * 若選擇 `EXP`：直接格式化要求輸入的日期為 `ExpiryDate`[cite: 13]。
       * **API 新增**：呼叫 `GAS ?action=addRecord&barcode=Barcode&productName=ProductName&capacity=capacity&notes=Notes&expiryDate=ExpiryDate` 並顯示結果[cite: 11]。
     * **[若失敗/查無此產品 (New Product)]**：
       * 透過提示要求輸入新編號 (`Barcode`) 之日英文品名 (`JPName`)[cite: 14]。
       * 透過要求輸入設定 `capacity` 容量[cite: 14]。
       * 透過要求輸入選擇日期 (`MFG`/`EXP`) 並計算/格式化出 `ExpiryDate`[cite: 14]。
       * **API 新增**：呼叫 `GAS ?action=addRecord&barcode=Barcode&productName=JPName&capacity=capacity&expiryDate=ExpiryDate&notes=Notes` 並顯示 URL 內容[cite: 12]。

### 2. 開封 (Open)
* **步驟說明**：
  1. 透過條碼要求文字並取得分割後的第一項作為 `Barcode`[cite: 14]。
  2. 呼叫 `GAS ?action=lookupProduct&barcode=Barcode`[cite: 14]。
  3. 從 URL 內容取得 `status` 數值[cite: 14]。
  4. 若狀態為 `success`：呼叫 `GAS ?action=openOil&barcode=Barcode` 並顯示結果[cite: 14]。
  5. 若查無此產品：顯示提示「查無此產品！請先到您的『商品對照表』工作表中建立此資料。」[cite: 14]

### 3. 用完 (Finished)
* **步驟說明**：
  1. 透過條碼要求文字並取得分割後的第一項作為 `Barcode`[cite: 12]。
  2. 呼叫 `GAS ?action=lookupProduct&barcode=Barcode` 取得產品資訊與狀態[cite: 12]。
  3. 若狀態成功：呼叫對應的狀態更新 API 並顯示回傳結果[cite: 12]。

---

## 三、 查看精油庫存模組

當選擇「查看精油庫存」時，會呼叫 `GAS ?action=getSummary` 取得摘要，並跳出子選單[cite: 10]：

### 1. 查詢單品詳情
* **步驟說明**：
  1. 執行「掃描行動條碼或馬碼」（Mac 不支援此動作，以手動輸入/文字替代）[cite: 10]。
  2. 呼叫 `GAS ?action=lookupProduct&barcode=...`[cite: 10]。
  3. 從回傳清單或字典中取得：`name`、`state`、`odate`、`edate`、`expired`、`notes`、`geminiPrompt`[cite: 10]。
  4. 將對應數值設為變數（`VarName`、`VarStatus`、`VarOpenDate`、`VarExpiryDate`、`VarIsExpired`、`VarNotes`、`geminiPrompt`）。
  5. **排版顯示**：透過內建文字樣板輸出精油詳細資訊：
     ```text
     🌿 精油詳細資訊 🌿 [geminiPrompt]
     -----------------------------
     品名：[VarName]
     狀態：[VarStatus]
     開封日期：[VarOpenDate]
     有效期限：[VarExpiryDate]
     是否過期：[VarIsExpired]
     備註：[VarNotes]
     ```
  6. 顯示上述文字。

### 2. 打開計算表
* **步驟說明**：
  1. 呼叫 `GAS ?action=getCSV` 取得內容。
  2. 將 URL 內容儲存到 Shortcuts 供檢視或串接。

---

## 四、 關鍵 GAS API 端點對照表

| 動作名稱 (`action`) | 傳入參數範例 | 說明 |
| :--- | :--- | :--- |
| `lookupProduct` | `barcode`[cite: 9, 14] | 依條碼查詢品名、容量與狀態 |
| `addRecord` | `barcode`, `productName`, `capacity`, `expiryDate`, `notes`[cite: 11, 12] | 新增精油庫存/進貨紀錄 |
| `openOil` | `barcode`[cite: 14] | 更新精油狀態為已開封 |
| `getSummary` | 無[cite: 10] | 取得整體庫存摘要 |
| `getCSV` | 無 | 取得試算表 CSV 數據 |

---

## 五、 全端系統整合與環境配置 (System Integration)

* **官方 Apple 捷徑名稱**：`精油庫存管理v4.0.3`
* **前端串接端點 (`static/inventory.js`)**：
  - URL Scheme：`shortcuts://run-shortcut?name=精油庫存管理v4.0.3`
  - 觸發情境：使用者於管理後台點選「📷 掃描」按鈕時，自動喚起原生 iOS 捷徑。
* **後端 Google 試算表資料母體**：
  - 試算表名稱：`精油対照表` / `在庫一覧`
  - 線上試算表連結：[精油対照表 Google Sheets](https://docs.google.com/spreadsheets/d/10VsNYwMoPsZBE7wO5JdhdpEnZw7ldk1FWbT7X5JkrXA/edit?usp=sharing)
* **GAS 核心程式碼檔**：
  - 程式碼路徑：[`shortcuts/JIN.md`](file:///d:/01_Project/GitHub/doterra/shortcuts/JIN.md)
  - 核心工作表常數：
    ```javascript
    const SHEET_NAME = "在庫一覧";
    const LOOKUP_SHEET = "精油対照表"; 
    const INFO_SHEET = "精油資訊表";
    ```
