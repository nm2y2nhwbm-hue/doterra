// ===================================================
// No.72.4 完整防呆與強健版 GAS 程式碼
// ===================================================

const SHEET_NAME = "在庫一覧";
const LOOKUP_SHEET = "精油対照表"; 
const INFO_SHEET = "精油資訊表";

function doGet(e) {
  // 防呆保護：如果直接在編輯器按執行導致 e 或 parameter 為空，直接返回提示
  if (!e || !e.parameter) {
    return ContentService.createTextOutput("⚠️ 提示：此指令必須透過 iOS 捷徑發送網址請求來觸發，無法直接在編輯器中執行。");
  }

  var params = e.parameter;
  var action = params.action || null;
  if (!action) return ContentService.createTextOutput("❌ 錯誤：缺少 Action 參數");

  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000);
    
    // 關鍵修正：確保 action 對應到正確的處理函式
    if (action === "lookupProduct") return handleLookupProduct(e);
    
    // 指令一：純新增 (入庫)
    if (action === "addRecord")     return handleProcessEntry(e, "未開封");
    
    // 指令二：開封變更 (從 未開封 -> 使用中)
    if (action === "openOil")       return handleOpenOil(e); 
    
    // 指令三：剩餘量編輯 (針對 使用中 進行變更)
    if (action === "emptyOil" || action === "markUsing") return handleUpdateLogic(e);

    return ContentService.createTextOutput("❌ 未知指令：" + action);
  } catch (err) {
    return ContentService.createTextOutput("⚠️ 系統錯誤：" + err.message);
  } finally { 
    lock.releaseLock(); 
  }
}

// --- ⚙️ 核心變更邏輯 ---
function handleUpdateLogic(e) {
  var rawBarcode = e.parameter.barcode || "";
  var barcode = cleanBarcode(rawBarcode);
  var notes = e.parameter.notes || "";
  
  Logger.log("接收到更新請求 - 原始條碼: [" + rawBarcode + "], 淨化後條碼: [" + barcode + "]");
  
  var resUsing = updateStatus(barcode, "使用中", "使用中", notes);
  if (resUsing.indexOf("✅") !== -1) return ContentService.createTextOutput(resUsing);
  
  var resOpen = updateStatus(barcode, "未開封", "使用中", notes);
  if (resOpen.indexOf("✅") !== -1) return ContentService.createTextOutput("💡 自動開瓶：" + resOpen);
  
  return ContentService.createTextOutput("❌ 變更失敗：在庫一覧中找不到「未開封」或「使用中」的 " + barcode);
}

function updateStatus(barcode, targetStatus, newStatus, notes) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  var searchID = cleanBarcode(barcode);
  
  var candidates = [];
  for (var i = 1; i < data.length; i++) {
    var rowID = cleanBarcode(data[i][1]);
    var rowStatus = data[i][4] ? data[i][4].toString().trim() : "";
    
    if (rowID === searchID && rowStatus === targetStatus) {
      var currentStock = parseInt(data[i][7] ? data[i][7].toString().match(/\d+/) : 100) || 100;
      candidates.push({ rowIdx: i + 1, stock: currentStock });
    }
  }

  if (candidates.length > 0) {
    candidates.sort((a, b) => a.stock - b.stock);
    var targetRow = candidates[0].rowIdx;
    
    var finalStatus = newStatus;
    if (notes && notes.match(/\d+/)) {
      var val = parseInt(notes.match(/\d+/)[0]);
      finalStatus = (val === 0 || notes.includes("空")) ? "已空瓶" : "使用中";
    }

    sheet.getRange(targetRow, 5).setValue(finalStatus);
    if (targetStatus === "未開封" && finalStatus === "使用中") {
      sheet.getRange(targetRow, 6).setValue(Utilities.formatDate(new Date(), "GMT+8", "yyyy/MM/dd HH:mm:ss"));
    }
    sheet.getRange(targetRow, 8).setValue(notes);

    autoSort(sheet);
    return "✅ 成功變更狀態為 " + finalStatus;
  }
  return "無數據";
}

// --- 🛠️ 專屬「開封」處理邏輯 ---
function handleOpenOil(e) {
  var rawBarcode = e.parameter.barcode || "";
  var barcode = cleanBarcode(rawBarcode);
  var timestamp = Utilities.formatDate(new Date(), "GMT+8", "yyyy/MM/dd HH:mm:ss");
  
  Logger.log("接收到開封請求 - 原始條碼: [" + rawBarcode + "], 淨化後條碼: [" + barcode + "]");
  
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  var data = sheet.getDataRange().getValues();
  
  var targetRow = -1;
  for (var i = 1; i < data.length; i++) {
    var rowID = cleanBarcode(data[i][1]);
    var rowStatus = data[i][4] ? data[i][4].toString().trim() : "";
    
    if (rowID === barcode && rowStatus === "未開封") {
      targetRow = i + 1;
      break;
    }
  }
  
  if (targetRow === -1) {
    return ContentService.createTextOutput("❌ 開封失敗：找不到狀態為「未開封」的 " + barcode + "（可能已開封或未入庫）。");
  }
  
  sheet.getRange(targetRow, 5).setValue("使用中");
  sheet.getRange(targetRow, 6).setValue(timestamp);
  
  autoSort(sheet);
  return ContentService.createTextOutput("✅ 成功開封並更新狀態為使用中");
}

function handleProcessEntry(e, defaultStatus) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  var lookupSheet = ss.getSheetByName(LOOKUP_SHEET);
  var barcode = cleanBarcode(e.parameter.barcode);
  var notes = e.parameter.notes || "";

  var lookupData = lookupSheet.getDataRange().getValues();
  var match = null;
  for (var i = 1; i < lookupData.length; i++) {
    if (cleanBarcode(lookupData[i][0]) === barcode) {
      match = { short: lookupData[i][3], cap: lookupData[i][2] };
      break;
    }
  }
  if (!match) return ContentService.createTextOutput("⚠️ 查無產品，請先至對照表建立 ID: " + barcode);

  var timestamp = Utilities.formatDate(new Date(), "GMT+8", "yyyy/MM/dd HH:mm:ss");
  sheet.appendRow([timestamp, barcode, match.short, match.cap, defaultStatus, (defaultStatus === "使用中" ? timestamp : ""), formatReiwa(e.parameter.expiryDate || ""), notes]);
  autoSort(sheet);
  return ContentService.createTextOutput("✅ [" + match.short + "] 新增成功");
}

function handleLookupProduct(e) {
  var searchKey = cleanBarcode(e.parameter.barcode);
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  var lookupSheet = ss.getSheetByName(LOOKUP_SHEET);
  var infoSheet = ss.getSheetByName(INFO_SHEET);

  var lookupData = lookupSheet.getDataRange().getValues();
  var base = null;
  for (var i = 1; i < lookupData.length; i++) {
    if (cleanBarcode(lookupData[i][0]) === searchKey) {
      base = { name: lookupData[i][3].toString().trim(), cap: lookupData[i][2] };
      break;
    }
  }
  if (!base) return createJsonResponse({"status": "error", "msg": "對照表查無此編號"});

  var advice = "⚠️ 尚無資訊表建議。";
  if (infoSheet) {
    var infoData = infoSheet.getDataRange().getValues();
    for (var k = 1; k < infoData.length; k++) {
      if (cleanBarcode(infoData[k][0]) === searchKey) {
        advice = `【${infoData[k][4]}】\n🌿 標籤：${infoData[k][2]}\n💧 塗抹：${infoData[k][3]}\n--------------------\n👨‍⚕️ 建議：\n${infoData[k][5]}`;
        break;
      }
    }
  }

  var stockData = sheet.getDataRange().getValues();
  var latest = { status: "無庫存", notes: "", expiry: "N/A", odate: "" };
  for (var j = stockData.length - 1; j >= 1; j--) {
    if (cleanBarcode(stockData[j][1]) === searchKey && stockData[j][4] !== "已空瓶") {
      latest = { status: stockData[j][4], notes: stockData[j][7], expiry: stockData[j][6], odate: stockData[j][5] };
      break;
    }
  }

  return createJsonResponse({ "status": "success", "name": base.name, "state": latest.status, "notes": latest.notes, "edate": latest.expiry, "odate": (latest.odate ? Utilities.formatDate(new Date(latest.odate), "GMT+8", "yyyy-MM-dd") : ""), "geminiPrompt": advice });
}

function autoSort(s) { 
  var lr = s.getLastRow(); 
  if (lr > 1) s.getRange(2,1,lr-1,8).sort([{column:5, ascending:true},{column:7, ascending:true}]); 
}

function cleanBarcode(b) { 
  if (!b) return "";
  return b.toString().trim().replace(/[\u3000]/g, "").split('|')[0].trim(); 
}

function formatReiwa(d) { 
  return d ? d.toString().trim().replace(/令和\s*(\d)年/, (m, p1) => "令和0" + p1 + "年") : ""; 
}

function createJsonResponse(o) { 
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); 
}

function handleEmptyOil(e) { 
  return handleUpdateLogic(e); 
}