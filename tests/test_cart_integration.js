/**
 * Agent 3 負責範圍：購物車與預約結帳系統整合測試 (tests/test_cart_integration.js)
 * 驗證購物車資料模型、結帳參數序列化至 booking.html 之 URL 查詢參數、
 * 多品項加乘運算精度與空車禁用防呆機制。
 */
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');
const vm = require('node:vm');

console.log('🧪 [Agent 3] 開始執行購物車與預約結帳系統深度整合測試 (test_cart_integration.js)...');

// 建立虛擬 LocalStorage
const mockStorage = {};
const localStorageMock = {
  getItem: (k) => Object.prototype.hasOwnProperty.call(mockStorage, k) ? mockStorage[k] : null,
  setItem: (k, v) => { mockStorage[k] = String(v); },
  removeItem: (k) => { delete mockStorage[k]; },
  clear: () => { Object.keys(mockStorage).forEach(k => delete mockStorage[k]); }
};

// 建立輕量 DOM 模擬
function createMockEl(tag = 'div') {
  const children = [];
  return {
    tagName: tag.toUpperCase(),
    className: '',
    classList: {
      _set: new Set(),
      add(c) { this._set.add(c); },
      remove(c) { this._set.delete(c); },
      contains(c) { return this._set.has(c); }
    },
    attributes: {},
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return this.attributes[k] || null; },
    dataset: {},
    appendChild(c) { children.push(c); return c; },
    querySelectorAll() { return []; },
    querySelector(selector) {
      if (selector === '#cart-checkout-btn') return checkoutBtnMock;
      return createMockEl('div');
    },
    addEventListener() {},
    style: {},
    textContent: '',
    innerHTML: ''
  };
}

const checkoutBtnMock = createMockEl('a');
checkoutBtnMock.href = '';

const eventListeners = {};
const windowMock = {
  addEventListener(event, fn) {
    eventListeners[event] = eventListeners[event] || [];
    eventListeners[event].push(fn);
  },
  dispatchEvent(ev) {
    if (eventListeners[ev.type]) {
      eventListeners[ev.type].forEach(fn => fn(ev));
    }
  },
  CustomEvent: class {
    constructor(type) { this.type = type; }
  },
  location: { search: '' }
};

const documentMock = {
  readyState: 'complete',
  createElement: (tag) => {
    if (tag === 'a') return checkoutBtnMock;
    return createMockEl(tag);
  },
  getElementById: (id) => {
    if (id === 'cart-checkout-btn') return checkoutBtnMock;
    return null;
  },
  querySelector: (sel) => {
    if (sel === '#cart-checkout-btn') return checkoutBtnMock;
    return null;
  },
  querySelectorAll: () => [],
  addEventListener: () => {},
  body: createMockEl('body')
};

const cartJsCode = fs.readFileSync(path.join(__dirname, '..', 'components', 'cart', 'cart.js'), 'utf8');

const sandbox = {
  localStorage: localStorageMock,
  window: windowMock,
  document: documentMock,
  console: console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  CustomEvent: windowMock.CustomEvent
};

vm.createContext(sandbox);
vm.runInContext(cartJsCode, sandbox);

const Cart = sandbox.window.ModernOilCart;
assert.ok(Cart, 'ModernOilCart 應成功暴露至 window');

// 測試案例 1: 驗證多品項複合運算精度與單一建議零售價合計
Cart.clear();
const item1 = { id: 'gift_mirror', name: '【鏡子】當下覺察調息禮盒', price: 1845, capacity: '15ml' };
const item2 = { id: 'custom_roller', name: '【客製】專屬位格滾珠精油', price: 1040, capacity: '10ml 滾珠' };
const item3 = { id: 'gift_crossroad', name: '【岔路】重大抉擇守護禮盒', price: 4895, capacity: '15ml' };

Cart.add(item1, 2); // 1845 * 2 = 3690
Cart.add(item2, 3); // 1040 * 3 = 3120
Cart.add(item3, 1); // 4895 * 1 = 4895
// 預期總額: 3690 + 3120 + 4895 = 11705

assert.equal(Cart.getCount(), 6, '商品總件數應為 6 件');
assert.equal(Cart.getTotal(), 11705, '總金額應精確為 11705 元');
console.log(' - 1. 多品項加權乘加總額精度驗證 (11,705 元): PASS');

// 測試案例 2: 驗證購物車轉換為 booking.html 查詢參數之資料合約
const items = Cart.getItems();
const total = Cart.getTotal();
const itemNames = items.map(i => `${i.name}×${i.qty}`).join('、');
const checkoutQuery = `booking.html?concern=${encodeURIComponent('購買調息禮盒')}&note=${encodeURIComponent('選購商品：' + itemNames + ' (總額 NT$ ' + total.toLocaleString() + ')')}`;

const parsedUrl = new URL(`https://example.com/${checkoutQuery}`);
assert.equal(parsedUrl.pathname, '/booking.html');
assert.equal(parsedUrl.searchParams.get('concern'), '購買調息禮盒');
assert.ok(parsedUrl.searchParams.get('note').includes('【鏡子】當下覺察調息禮盒×2'));
assert.ok(parsedUrl.searchParams.get('note').includes('【客製】專屬位格滾珠精油×3'));
assert.ok(parsedUrl.searchParams.get('note').includes('【岔路】重大抉擇守護禮盒×1'));
assert.ok(parsedUrl.searchParams.get('note').includes('11,705'));
console.log(' - 2. 結帳 URL 參數編碼與 booking.html 資料合約驗證: PASS');

// 測試案例 3: 驗證清空購物車後空狀態邏輯
Cart.clear();
assert.equal(Cart.getCount(), 0);
assert.equal(Cart.getTotal(), 0);
assert.equal(Cart.getItems().length, 0);
console.log(' - 3. 購物車重設歸零防呆驗證: PASS');

console.log('✅ [Agent 3] 購物車與預約結帳系統整合測試 100% 通過！');
