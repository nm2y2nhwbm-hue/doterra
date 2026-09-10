# 📋 Agent 3 全站品質稽核發現與跨 Agent 協同優化備忘錄 (QA Collaboration Memo)

> **發布者**：Agent 3（品管與測試工程師）  
> **發布日期**：2026-09-10  
> **適用範圍**：全專案五大代理人協作體系（Agent 1、Agent 2、Agent 4、Agent 5）  
> **宗旨**：依據日式款待美學（Omotenashi / 侘寂 / 間 / 所作）、無障礙無損閱讀標準（WCAG AA）與全站系統架構，提供跨領域工程師之具體優化建議與檔案坐標。

---

## 🎨 一、建請 Agent 2（前端切版工程師）協同優化項

### 1.1 `style.css` 雙 `:root` 宣告整併（消滅樣式覆寫飄移）
- **檔案坐標**：[`static/style.css:L6-L42`](file:///c:/Users/User/Documents/GitHub/doterra/static/style.css#L6-L42)
- **稽核發現**：
  目前在第 6 行與第 32 行存在兩組 `:root` 宣告，導致若干設計標記被重複定義微調：
  - 第 7 行 `--paper: #F8F4EC;` ➔ 第 34 行覆寫為 `--paper: #F6F1E7;`
  - 第 11 行 `--forest: #435B48;` ➔ 第 36 行覆寫為 `--forest: #4B6350;`
  - 第 19 行 `--nav-h: 62px;` ➔ 第 39 行覆寫為 `--nav-h: 56px;`
- **建議方案**：
  整併為單一標準 `:root` 區塊，並以傳統日式和色嚴格規範命名：
  - **胡粉（Gofun）**：`--paper-light: #FAF6EC;`（頁面頂部柔光）
  - **白茶（Shiracha）**：`--paper: #F6F1E7;`（主背景底色）
  - **利休白茶（Rikyu-shiracha）**：`--paper-deep: #ECE3D2;`（卡片底色與抽屜背景）
  - **常磐綠（Tokiwa-midori）**：`--forest-deep: #253B2F;`（深邃主文字與主按鈕）
  - **蒔繪金（Makie-gold）**：`--gold: #B8912E;`、`--gold-hairline: rgba(184, 145, 46, 0.22);`（細線金箔描邊）

---

### 1.2 「間 (Ma)」動態留白與文字避頭尾排版
- **檔案坐標**：[`static/style.css`](file:///c:/Users/User/Documents/GitHub/doterra/static/style.css)
- **稽核發現**：
  行高 `1.95` 已具備良好的呼吸感，但在寬度小於 360px 的行動螢幕時，部分卡片內距顯得稍緊湊。
- **建議方案**：
  1. **流體邊距（Fluid Spacing）**：在 `@media (max-width: 480px)` 引入 `padding: clamp(14px, 3.5vw, 22px);`。
  2. **文字避頭尾（Orphan Prevention）**：在卡片正文段落（如 `.card-description`、`.oracle-guidance`）啟用 `text-wrap: pretty;` 或 `text-wrap: balance;`，杜絕單一字元孤立換行，維護日本印刷級的視覺雅緻。

---

### 1.3 「所作 (Shosa)」與「殘心 (Zanshin)」微互動
- **檔案坐標**：[`components/cart/cart.css`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.css)、[`components/cart/cart.js`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.js)
- **稽核發現**：
  目前購物車按鈕下壓 `scale(0.96)` 與加車彈跳已具備良好手感。
- **建議方案**：
  1. **導入「殘心（餘韻）」**：購物車 Toast 提示（`showToast`）在 2.5 秒倒數完畢時，建議加入煙嵐消散般的高斯模糊淡出（`filter: blur(4px); opacity: 0; transition: all 0.4s var(--ease-zen);`），而非突兀隱藏。
  2. **紙紋質感（Washi Texture）**：抽屜背景或彈窗可引入微弱的紙紋燥點，營造和紙溫潤觸感。

---

## 📜 二、建請 Agent 4（商品與文案主編）協同評估項

### 2.1 款待（Omotenashi）文案幽玄化修潤
- **檔案坐標**：[`static/index.html`](file:///c:/Users/User/Documents/GitHub/doterra/static/index.html)、[`components/cart/cart.js`](file:///c:/Users/User/Documents/GitHub/doterra/components/cart/cart.js)
- **建議評估**：
  在保持流程直觀易懂的前提下，評估將部分電商術語微調為自然調息雅緻用詞：
  - 「加入購物車」 ➔ **「納入調息選品」** 或保持「加入調息清單」
  - 「前往結帳」 ➔ **「前往預約調息行囊」** 或 **「確認香氣選品」**
  - 目前購物車為空提示「目前尚未挑選香氣商品，讓直覺帶你探索」文筆極為優美，建請全站維持此種安靜沉穩之語調。

---

## 🛡️ 三、建請 Agent 1（後端工程師）協同維護項

### 3.1 精油 SKU 編號補全追蹤
- **檔案坐標**：[`doterra.csv`](file:///c:/Users/User/Documents/GitHub/doterra/doterra.csv)
- **稽核發現**：
  經 `tests/test_catalog_integrity.py` 掃描，目前尚有 9 筆精油標記為 `(待補)`。測試已建立防呆追蹤機制，不影響日常運作；建請 Agent 1 / 4 後續於官方資料齊全時統一補上標準 8 位數官方代碼。

---

## 💳 四、建請 Agent 5（維運與金流工程師）協同優化項

### 4.1 邊緣 CDN 快取標頭與 HSTS 安全
- **檔案坐標**：[`infra/cloud_specs.md`](file:///c:/Users/User/Documents/GitHub/doterra/infra/cloud_specs.md)、[`static/vercel.json`](file:///c:/Users/User/Documents/GitHub/doterra/static/vercel.json)
- **建議方案**：
  建請確保根目錄配置標準 `vercel.json`，將 `X-Frame-Options: SAMEORIGIN` 與 `Strict-Transport-Security` 廣播至所有邊緣端點，使全站探測標頭維持 A+ 安全評級。

---

## 🧪 五、Agent 3（品管與測試）自家守護承諾

為配合上述日式款待與品質規範，Agent 3 已在自家 [`tests/test_asset_integrity.py`](file:///c:/Users/User/Documents/GitHub/doterra/tests/test_asset_integrity.py) 完成了兩大守護防線實裝：
1. **`test_japanese_color_contrast_ratio()`**：以 W3C 相對亮度公式驗證暖米底與常磐深綠文字之色彩對比度達 **`10.28:1`**（遠高於 WCAG AA 4.5:1），確保視覺古典的同時長輩也能清晰閱讀。
2. **`test_zen_design_tokens_and_motion()`**：強制稽核全站日式 Design Tokens 與 `cubic-bezier(0.22, 1, 0.36, 1)` 禪意過渡無缺漏。
3. **`tests/run_all_tests.py`**：全量 11 套深度測試持續守護，維持 100% 綠燈秒級驗收。
