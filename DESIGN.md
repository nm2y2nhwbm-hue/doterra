# Design System: 雫之洞悉 · 返魂堂 (現代精油心靈指引卡 · Modern Oil Oracle)
**Project ID:** 5923035553865007790

## 1. Visual Theme & Atmosphere
「雫之洞悉 · 返魂堂」融合東方日式侘寂（Wabi-sabi）哲學與現代自然醫學款待（Omotenashi）美學。整體視覺風格呈現靜謐、深邃且溫暖的沉浸氛圍，如同走入京都傳統木造芳香町家。界面講究留白節奏、細膩流光與呼吸般的微互動，排版注重縱橫書寫的墨韻對齊，引導使用者卸下防備、覺察當下身心狀態。

## 2. Color Palette & Roles
* **琉璃竹青 (Forest Bamboo Green) (`#355343`):** 品牌主要身心主色，用於頂部主標題、主行動按鈕（Primary Buttons）、主導航元素與高階品牌象徵。
* **和紙象牙白 (Washi Rice Paper) (`#fdfcf7`):** 淺色主題底色，帶有極細微纖維質感的溫潤米白，用於整體頁面背景與內容底襯。
* **蒔繪金箔 (Maki-e Gold Leaf) (`#c5a059` / `#d4af37`):** 奢華款待金，用於牌卡邊框、精油禮盒金飾、徽章外圈與 Hover 流光特效。
* **深緋朱紅 (Akane Crimson) (`#8b263e` / `#a9324e`):** 核心脈動色，用於特別警示、脈輪能量標記與關鍵促購按鈕。
* **墨黑深炭 (Sumi Ink Charcoal) (`#1e2022`):** 高對比主文字色，用於大標題、正文內容與高清晰度標籤。
* **薄雲霧灰 (Mist Paper Gray) (`#f3efe6` / `#e9e4d8`):** 次級背景與邊框分隔色，用於卡片背景、表格交錯底色與微弱輪廓線。
* **苔嵐青灰 (Moss Slate) (`#6b7f73`):** 輔助中性色，用於英文副標、輔助描述說明與未選中狀態。
* **LINE Pay 款待綠 (LINE Pay Green) (`#06c755`):** 專屬結帳金流主色，用於一鍵快速結帳按鈕與授權安全標章。

## 3. Typography Rules
* **中文標題族 (Display Headings):** `Noto Serif TC`、`Shippori Mincho`、宋體/明體。大字重 600~700，字距寬闊（`letter-spacing: 0.08em ~ 0.15em`），彰顯日式職人風骨與靈性儀式感。
* **正文與數據 (Body & Numbers):** `Plus Jakarta Sans`、`Inter`、`Noto Sans TC`。字重 400~500，行高 1.6~1.8，字距 0.02em，保持長時間閱覽之舒適度。
* **籤詩與指引 (Poetic Guidance):** 斜體或直書排版感、和風四字熟語、居中詩意對齊。

## 4. Component Stylings
* **主按鈕 (Buttons):** 膠囊型（`rounded-full`）或精緻圓角（`rounded-lg`），背景為琉璃青 (`#355343`) 或金茶箔光，觸控時具有阻尼微幅下壓回饋（`-translate-y-0.5`）。
* **卡牌容器 (Cards & Containers):** 圓角 `rounded-2xl`，和紙白襯底，外緣帶有 `1px solid rgba(197, 160, 89, 0.25)` 之極細金茶微光，陰影使用超柔和漫反射 `0 4px 20px rgba(0,0,0,0.06)`。
* **導覽列 (Top Navigation):** 毛玻璃磨砂半透明懸浮條（`backdrop-filter: blur(12px)`，`background: rgba(253, 252, 247, 0.92)`），左側帶有返魂堂金箔紋章（Logo Emblem）。
* **購物車抽屜 (Cart Drawer):** 右側平滑滑出抽屜，內嵌日式款待過渡層（`.linepay-transition-overlay`），支援 LINE Pay 沙盒一鍵結帳。
* **表單與輸入框 (Inputs & Forms):** 扁平細線輪廓，聚焦時顯現金茶微光光暈（`ring-1 ring-[#c5a059]`），背景淡雅和紙白。

## 5. Layout Principles
* **禪意留白 (Zen Spacing):** 區塊間保留大面積留白（`py-16 md:py-24`），段落與卡片間距均勻呼應。
* **多端響應適配:** 行動端支援 iOS Safe Area 底部墊高、42px+ 無障礙觸控熱區；桌面端支援最高 1200px 居中容器與多欄流式網格。
