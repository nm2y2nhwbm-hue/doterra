/**
 * Agent 3 負責範圍：前端購物車狀態管理與價格計算單元測試 (tests/test_cart_logic.js)
 */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const cartJsPath = path.join(__dirname, '..', 'components', 'cart', 'cart.js');
const source = fs.readFileSync(cartJsPath, 'utf8');

// 模擬 LocalStorage
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null;
  }
  setItem(key, value) {
    this.store[key] = String(value);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

// 建立輕量級 DOM 元素模擬
function createMockElement(tag = 'div') {
  const children = [];
  const el = {
    tagName: tag.toUpperCase(),
    className: '',
    classList: {
      _classes: new Set(),
      add(cls) { this._classes.add(cls); },
      remove(cls) { this._classes.delete(cls); },
      contains(cls) { return this._classes.has(cls); },
    },
    attributes: {},
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return this.attributes[k] || null; },
    dataset: {},
    appendChild(child) {
      children.push(child);
      return child;
    },
    querySelectorAll(selector) {
      return [];
    },
    querySelector(selector) {
      // 依 ID 或 Class 簡易返回 mock 子元素
      return createMockElement('div');
    },
    addEventListener() {},
    style: {},
    innerHTML: '',
    textContent: '',
  };
  return el;
}

// 模擬瀏覽器環境
function createMockEnvironment() {
  const localStorage = new MockLocalStorage();
  const events = [];

  const mockDoc = {
    readyState: 'complete',
    createElement: createMockElement,
    body: createMockElement('body'),
    querySelectorAll: () => [],
    querySelector: () => createMockElement('div'),
    addEventListener: () => {},
    dispatchEvent: (event) => events.push(event),
  };

  const mockWindow = {
    addEventListener: () => {},
    dispatchEvent: (event) => events.push(event),
    localStorage,
  };

  class MockCustomEvent {
    constructor(type, init = {}) {
      this.type = type;
      this.detail = init.detail || {};
    }
  }

  const context = {
    window: mockWindow,
    document: mockDoc,
    localStorage,
    CustomEvent: MockCustomEvent,
    console: {
      log: () => {},
      warn: () => {},
      error: console.error,
    },
    setTimeout: (fn) => setTimeout(fn, 0),
    clearTimeout: () => {},
  };

  vm.runInNewContext(source, context, { filename: 'cart.js' });
  return { cart: context.window.ModernOilCart, localStorage, events };
}

// 執行測試套件
console.log('🧪 [Agent 3] 開始執行購物車核心邏輯單元測試 (test_cart_logic.js)...');

const { cart, localStorage } = createMockEnvironment();
assert(cart, 'window.ModernOilCart 必須成功暴露');

// 1. 初始化狀態驗證
assert.equal(cart.getCount(), 0, '初始商品總數應為 0');
assert.equal(cart.getTotal(), 0, '初始商品總金額應為 0');
assert.equal(cart.getItems().length, 0, '初始購物車清單長度應為 0');

// 2. 新增品項測試
const productA = {
  id: 'gift-mirror',
  name: '【鏡子】當下覺察調息禮盒',
  price: 1845,
  capacity: '15ml × 2',
  pillar: '中柱平衡',
  image: 'images/gift-mirror.png',
};
cart.add(productA, 1);

assert.equal(cart.getCount(), 1, '加入 1 件商品後總數應為 1');
assert.equal(cart.getTotal(), 1845, '加入禮盒後總金額應為 1845');
assert.equal(cart.getItems().length, 1, '商品品項清單長度應為 1');
assert.equal(cart.getItems()[0].name, '【鏡子】當下覺察調息禮盒');

// 3. 重複加入同一品項累加數量測試
cart.add(productA, 2);
assert.equal(cart.getCount(), 3, '重複加入 2 件後總數應為 3');
assert.equal(cart.getTotal(), 1845 * 3, '總金額應為 1845 * 3 = 5535');
assert.equal(cart.getItems().length, 1, '品項長度應維持 1（僅更新 qty）');

// 4. 新增第二項商品與總金額加乘測試
const productB = {
  id: 'oil-lavender',
  name: '真正薰衣草 Lavender',
  price: 1310,
  capacity: '15ml',
  pillar: '中柱平衡',
};
cart.add(productB, 1);
assert.equal(cart.getCount(), 4, '品項累計總數應為 4 (3 + 1)');
assert.equal(cart.getTotal(), (1845 * 3) + 1310, '總金額應為 5535 + 1310 = 6845');
assert.equal(cart.getItems().length, 2, '應存在 2 種不同商品');

// 5. 數量增減測試 (updateQty)
cart.updateQty('gift-mirror', 1);
assert.equal(cart.getCount(), 5, '增加 1 件後總數應為 5');

cart.updateQty('gift-mirror', -2);
assert.equal(cart.getCount(), 3, '減少 2 件後總數應為 3');

// 6. 數量減至 0 以下自動移除測試
cart.updateQty('oil-lavender', -1);
assert.equal(cart.getItems().length, 1, '數量歸零後該品項應自動自清單中移除');
assert.equal(cart.getItems().some(i => i.id === 'oil-lavender'), false);

// 7. 單一手動移除測試 (remove)
const productC = { id: 'oil-lemon', name: '檸檬 Lemon', price: 630 };
cart.add(productC, 1);
assert.equal(cart.getItems().length, 2);
cart.remove('gift-mirror');
assert.equal(cart.getItems().length, 1);
assert.equal(cart.getItems()[0].id, 'oil-lemon');

// 8. 清空購物車測試 (clear)
cart.clear();
assert.equal(cart.getCount(), 0, '清空後數量應為 0');
assert.equal(cart.getTotal(), 0, '清空後總額應為 0');
assert.equal(cart.getItems().length, 0, '清空後清單應為空');

// 9. LocalStorage 資料持久性驗證
const savedRaw = localStorage.getItem('modern_oil_cart');
assert.equal(savedRaw, '[]', '清空後 LocalStorage 應儲存為 []');

cart.add({ id: 'test-item', name: '測試商品', price: 100 }, 2);
const updatedRaw = JSON.parse(localStorage.getItem('modern_oil_cart'));
assert.equal(updatedRaw.length, 1);
assert.equal(updatedRaw[0].id, 'test-item');
assert.equal(updatedRaw[0].qty, 2);
assert.equal(updatedRaw[0].price, 100);

console.log('✅ [Agent 3] 購物車所有 9 項單元測試 100% 通過！');
