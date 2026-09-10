# 📖 精油圖鑑與自然醫學調息彈窗元件 (`components/oils-catalog/`)

本目錄為 **Agent 2（前端切版工程師）** 負責維護之 131 款精油圖鑑 Modal、生命之樹三大位格印章與自然醫學調息箋展開元件。

---

## 📌 元件清單
- **`insight-modal.html`**：日式和紙風格彈窗模板（包含卡牌圖鑑、SKU、位格印章、容量、建議零售價、塗抹安全等級、自然醫學調息指引、心靈指引與脈輪）。
- **`insight-modal.css`**：毛玻璃背景遮罩、蒔繪金線外框、印章色票與行動版自適應樣式。
- **`insight-modal.js`**：彈窗開關控制、無障礙焦點陷阱（Focus Trap）、鍵盤 `Escape` 監聽與 `ModernOilCart` 加購聯動。

---

## 🏛️ 三大位格印章規範 (Tree of Life Pillars)

1. **☯️ 中柱 · 平衡 (Balance)**：
   - 樣式 class：`.tag-balance`
   - 色彩調性：常磐綠底色 `rgba(75, 99, 80, 0.12)`、深綠字體 `#2D4232`。
2. **☀️ 右柱 · 慈悲 (Mercy)**：
   - 樣式 class：`.tag-mercy`
   - 色彩調性：琥珀金底色 `rgba(184, 145, 46, 0.14)`、金褐字體 `#785A12`。
3. **🌙 左柱 · 嚴厲 (Severity)**：
   - 樣式 class：`.tag-severity`
   - 色彩調性：灰藍墨底色 `rgba(60, 80, 100, 0.12)`、深墨藍字體 `#243545`。

---

## 🛡️ 塗抹安全等級印章 (Dilution Guide)

- **🌿 直塗可** (`.safety-direct`)：溫和親膚，可直接以原精油塗抹。
- **⚠️ 敏感需稀釋** (`.safety-sensitive`)：易敏膚質建議以分餾椰子油稀釋後塗抹。
- **💧 必須稀釋** (`.safety-dilute`)：具強烈活血或刺激性，務必經載體油稀釋後方能使用。

---

## 🚀 JavaScript API 呼叫範例

```javascript
// 引入 insight-modal.js 後，呼叫 open 方法傳入精油物件
window.ModernOilInsightModal.open({
  sku: "60200143",
  name: "野橘精油",
  name_en: "Wild Orange",
  pillar: "中柱 · 平衡",
  capacity: "15ml",
  price: 590,
  usage_tags: "A T I",
  dilution_guide: "直塗",
  doctor_advice: "主調和身心、舒緩壓力與提振愉悅頻率。",
  guidance: "敞開心胸，擁抱純粹的豐盛與創造力。",
  chakra: "臍輪",
  image_filename: "wild-orange.jpg"
});

// 關閉彈窗
window.ModernOilInsightModal.close();
```
