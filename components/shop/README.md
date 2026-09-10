# 🛍️ 調息香氣選品元件 (`components/shop/`)

本目錄為 **Agent 2（前端切版工程師）** 負責維護之首頁「調息香氣選品」模組，呈現結合三大牌陣與生命之樹位格的 4 款精油禮盒。

---

## 📌 元件清單
- **`shop.html`**：4 大禮盒卡片語意化 HTML5 結構與 `data-cart-item` 購物協議定義。
- **`shop.css`**：日式款待美學卡片網格、蒔繪金線外框與懸停反饋樣式。

---

## 💎 4 大商品規格審定與對應

| 商品編號 (SKU) | 禮盒名稱 | 牌陣與位格對應 | 官方容量規格 | 建議零售價 (NT$) |
| :--- | :--- | :--- | :--- | :--- |
| `SET-MIRROR-01` | 【鏡子】當下覺察調息禮盒 | 🪞 鏡子 · 中柱平衡 | 15ml×2（野橘 + 安定平衡） | $1,845 |
| `SET-RIVER-02` | 【河流】時間軌跡梳理禮盒 | 🌊 河流 · 右柱慈悲 | 15ml×2（高山雪松 + 順暢清新） | $1,965 |
| `SET-CROSS-03` | 【岔路】重大抉擇守護禮盒 | ⛩️ 岔路 · 左柱嚴厲 | 15ml+10ml滾珠（神聖乳香 + 舒壓複方） | $4,895 |
| `CUSTOM-ROLLER-10` | 【客製】專屬位格滾珠精油 | 💎 位格特調 | 10ml 隨身滾珠（依抽牌位格現調） | $1,040 |

> **合規守則**：所有容量皆遵循官方標準（`15ml`、`5ml`、`10ml滾珠`、`115ml`），價格嚴格符合 Agent 4 所審定之單一官方建議零售價。

---

## 🔌 購物車協議 (`data-cart-item`)

按鈕採用聲明式 HTML 屬性與 `components/cart/cart.js` 自動聯動：

```html
<button type="button" 
        class="shop-add-btn" 
        data-add-cart 
        data-cart-item='{"id":"SET-MIRROR-01","name":"【鏡子】當下覺察調息禮盒","price":1845,"capacity":"15ml×2","pillar":"中柱 · 平衡","image":"images/logo-emblem.png"}'>
  <span>＋ 加入清單</span>
</button>
```

- **`data-add-cart`**：委派事件觸發標記。
- **`data-cart-item`**：包含 `id`, `name`, `price` (整數), `capacity`, `pillar`, `image` 之 JSON 字串。
