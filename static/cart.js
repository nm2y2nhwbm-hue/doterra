/**
 * 雫之洞悉 · 返魂堂 · 全站購物車與商品邏輯 (cart.js)
 */
(function() {
  'use strict';

  const STORAGE_KEY = 'modern_oil_cart';

  function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function sanitizeUrl(url) {
    if (!url) return 'images/logo-emblem.png';
    const clean = String(url).trim();
    if (/^(https?:\/\/|\/|images\/)/i.test(clean)) {
      return clean.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }
    return 'images/logo-emblem.png';
  }

  // 購物車資料管理
  const CartStore = {
    get() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
      } catch (e) {
        console.error('[Cart] 讀取購物車失敗', e);
        return [];
      }
    },
    save(items) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        window.dispatchEvent(new CustomEvent('cart:updated', { detail: { items } }));
      } catch (e) {
        console.error('[Cart] 儲存購物車失敗', e);
      }
    },
    add(product, qty = 1) {
      const items = this.get();
      const existing = items.find(i => String(i.id) === String(product.id));
      if (existing) {
        existing.qty = Math.max(1, (existing.qty || 1) + qty);
      } else {
        items.push({
          id: String(product.id),
          name: product.name || '調息香氣選品',
          price: Number(product.price) || 0,
          capacity: product.capacity || '',
          pillar: product.pillar || '',
          image: product.image || 'images/logo-emblem.png',
          qty: Math.max(1, qty)
        });
      }
      this.save(items);
      showToast(`已將「${product.name}」加入調息清單`);
      triggerCartBounce();
    },
    remove(id) {
      let items = this.get();
      items = items.filter(i => String(i.id) !== String(id));
      this.save(items);
    },
    updateQty(id, delta) {
      const items = this.get();
      const item = items.find(i => String(i.id) === String(id));
      if (!item) return;
      item.qty += delta;
      if (item.qty <= 0) {
        this.remove(id);
      } else {
        this.save(items);
      }
    },
    clear() {
      this.save([]);
    },
    count() {
      return this.get().reduce((sum, i) => sum + (i.qty || 1), 0);
    },
    total() {
      return this.get().reduce((sum, i) => sum + ((i.price || 0) * (i.qty || 1)), 0);
    }
  };

  // Toast 提示通知
  let toastEl = null;
  let toastTimer = null;
  function showToast(msg) {
    if (!toastEl) {
      toastEl = document.createElement('div');
      toastEl.className = 'cart-toast';
      document.body.appendChild(toastEl);
    }
    toastEl.textContent = msg;
    toastEl.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastEl.classList.remove('show');
    }, 2400);
  }

  // 建立抽屜與懸浮按鈕 DOM
  let floatBtn, drawerEl, backdropEl, badgeEl, listEl, totalEl, checkoutBtn;

  function triggerCartBounce() {
    if (floatBtn && floatBtn.classList) {
      floatBtn.classList.remove('bounce');
      if (typeof floatBtn.offsetWidth !== 'undefined') {
        void floatBtn.offsetWidth;
      }
      floatBtn.classList.add('bounce');
      setTimeout(() => {
        if (floatBtn && floatBtn.classList) floatBtn.classList.remove('bounce');
      }, 700);
    }
    if (badgeEl && badgeEl.classList) {
      badgeEl.classList.remove('pop');
      if (typeof badgeEl.offsetWidth !== 'undefined') {
        void badgeEl.offsetWidth;
      }
      badgeEl.classList.add('pop');
      setTimeout(() => {
        if (badgeEl && badgeEl.classList) badgeEl.classList.remove('pop');
      }, 400);
    }
  }

  function initUI() {
    // 1. 懸浮按鈕
    floatBtn = document.createElement('button');
    floatBtn.className = 'floating-cart-btn';
    floatBtn.setAttribute('type', 'button');
    floatBtn.setAttribute('aria-label', '查看調息購物清單');
    floatBtn.innerHTML = `
      <svg viewBox="0 0 24 24" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="9" cy="21" r="1"></circle>
        <circle cx="20" cy="21" r="1"></circle>
        <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
      </svg>
      <span class="cart-badge-count" id="cart-badge">0</span>
    `;
    document.body.appendChild(floatBtn);
    badgeEl = floatBtn.querySelector('#cart-badge');

    // 2. 遮罩
    backdropEl = document.createElement('div');
    backdropEl.className = 'cart-backdrop';
    document.body.appendChild(backdropEl);

    // 3. 抽屜面板
    drawerEl = document.createElement('div');
    drawerEl.className = 'cart-drawer';
    drawerEl.setAttribute('role', 'dialog');
    drawerEl.setAttribute('aria-modal', 'true');
    drawerEl.setAttribute('aria-label', '調息購物清單');
    drawerEl.innerHTML = `
      <div class="cart-drawer-header">
        <div class="cart-drawer-title">
          <span>💧</span>
          <span>調息選品清單</span>
        </div>
        <button type="button" class="cart-close-btn" id="cart-close-btn" aria-label="關閉清單">✕</button>
      </div>
      <div class="cart-drawer-body" id="cart-items-container"></div>
      <div class="cart-drawer-footer">
        <div class="cart-summary-row">
          <span class="cart-summary-label">合計金額</span>
          <span class="cart-total-amount" id="cart-total-amount">NT$ 0</span>
        </div>
        <div class="cart-shipping-tip">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
          <span>全館調息禮盒享日式款待包裝與專人體驗安排</span>
        </div>
        <a href="booking.html" class="cart-checkout-btn" id="cart-checkout-btn">
          <span>前往預約與配送結帳</span>
          <span>→</span>
        </a>
        <button type="button" class="cart-clear-link" id="cart-clear-btn">清空所有選品</button>
      </div>
    `;
    document.body.appendChild(drawerEl);

    listEl = drawerEl.querySelector('#cart-items-container');
    totalEl = drawerEl.querySelector('#cart-total-amount');
    checkoutBtn = drawerEl.querySelector('#cart-checkout-btn');

    // 事件監聽
    floatBtn.addEventListener('click', openDrawer);
    backdropEl.addEventListener('click', closeDrawer);
    drawerEl.querySelector('#cart-close-btn').addEventListener('click', closeDrawer);
    drawerEl.querySelector('#cart-clear-btn').addEventListener('click', () => {
      if (confirm('確定清空調息購物清單嗎？')) {
        CartStore.clear();
      }
    });

    // 鍵盤 Escape 關閉
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && drawerEl.classList.contains('open')) {
        closeDrawer();
      }
    });

    // 行動版向右輕滑關閉抽屜手勢 (Swipe-to-Dismiss)
    let touchStartX = 0;
    let touchStartY = 0;
    let touchDiffX = 0;

    drawerEl.addEventListener('touchstart', (e) => {
      if (!drawerEl.classList.contains('open') || !e.touches || !e.touches[0]) return;
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      touchDiffX = 0;
    }, { passive: true });

    drawerEl.addEventListener('touchmove', (e) => {
      if (!drawerEl.classList.contains('open') || !e.touches || !e.touches[0]) return;
      const currentX = e.touches[0].clientX;
      const currentY = e.touches[0].clientY;
      const dx = currentX - touchStartX;
      const dy = Math.abs(currentY - touchStartY);
      if (dx > 0 && dx > dy) {
        touchDiffX = dx;
      }
    }, { passive: true });

    drawerEl.addEventListener('touchend', () => {
      if (touchDiffX > 60) {
        closeDrawer();
      }
      touchDiffX = 0;
    }, { passive: true });

    // 導覽列若有 .nav-cart-btn 也一併綁定
    document.querySelectorAll('.nav-cart-link').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        openDrawer();
      });
    });

    renderUI();
  }

  function openDrawer() {
    renderUI();
    drawerEl.classList.add('open');
    backdropEl.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawerEl.classList.remove('open');
    backdropEl.classList.remove('open');
    document.body.style.overflow = '';
  }

  function renderUI() {
    const items = CartStore.get();
    const count = CartStore.count();
    const total = CartStore.total();

    // 更新角標
    if (badgeEl) {
      badgeEl.textContent = count;
      if (count > 0) {
        badgeEl.classList.add('show');
      } else {
        badgeEl.classList.remove('show');
      }
    }

    // 更新導覽列角標（若有）
    document.querySelectorAll('.nav-cart-count').forEach(badge => {
      badge.textContent = count;
      badge.style.display = count > 0 ? 'inline-block' : 'none';
    });

    // 更新總金額
    if (totalEl) {
      totalEl.textContent = `NT$ ${total.toLocaleString()}`;
    }

    // 更新結帳連結（帶參數至 booking.html）
    if (checkoutBtn) {
      if (items.length > 0) {
        const itemNames = items.map(i => `${i.name}×${i.qty}`).join('、');
        checkoutBtn.href = `booking.html?concern=${encodeURIComponent('購買調息禮盒')}&note=${encodeURIComponent('選購商品：' + itemNames + ' (總額 NT$ ' + total.toLocaleString() + ')')}`;
        checkoutBtn.style.opacity = '1';
        checkoutBtn.style.pointerEvents = 'auto';
      } else {
        checkoutBtn.href = 'booking.html';
        checkoutBtn.style.opacity = '0.6';
        checkoutBtn.style.pointerEvents = 'none';
      }
    }

    // 渲染清單
    if (!listEl) return;
    if (items.length === 0) {
      listEl.innerHTML = `
        <div class="cart-empty-state">
          <div class="cart-empty-icon-wrap">
            <svg class="cart-zen-svg" viewBox="0 0 64 64" fill="none" stroke="currentColor">
              <ellipse cx="32" cy="46" rx="22" ry="7" stroke-width="1.2" stroke-dasharray="2 3" opacity="0.4"/>
              <ellipse cx="32" cy="46" rx="14" ry="4.5" stroke-width="1.4" opacity="0.6"/>
              <path d="M32 14 C32 14 20 30 20 38 C20 44.6 25.4 50 32 50 C38.6 50 44 44.6 44 38 C44 30 32 14 32 14 Z" stroke-width="1.8" fill="rgba(184,145,46,0.06)"/>
              <circle cx="32" cy="36" r="3" fill="var(--gold-accent, #C5A059)" opacity="0.75"/>
            </svg>
          </div>
          <div class="cart-empty-haiku">「風止香在 · 靜待直覺」</div>
          <div class="cart-empty-title">目前尚未挑選調息逸品</div>
          <div class="cart-empty-sub">給心靈片刻留白，讓直覺指引卡帶您探索當下所需的神聖香氣。</div>
          <a class="home-cta primary cart-empty-cta" href="cards.html" onclick="window.ModernOilCart.close()">
            <span>🔮 線上直覺抽卡指引</span>
          </a>
        </div>
      `;
      return;
    }

    listEl.innerHTML = items.map(item => {
      const id = escapeHtml(item.id || '');
      const name = escapeHtml(item.name || '調息選品');
      const img = sanitizeUrl(item.image);
      const pillar = escapeHtml(item.pillar || '');
      const capacity = escapeHtml(item.capacity || '');
      const price = Number(item.price) || 0;
      const qty = Math.max(1, Number(item.qty) || 1);
      const subtotal = (price * qty).toLocaleString();

      return `
      <div class="cart-item-card" data-id="${id}">
        <img class="cart-item-thumb" src="${img}" alt="${name}">
        <div class="cart-item-info">
          <div class="cart-item-title-row">
            <div>
              <div class="cart-item-name">${name}</div>
              ${pillar ? `<div class="cart-item-pillar">${pillar}</div>` : ''}
              ${capacity ? `<div style="font-size:11px;color:#8E867E;">${capacity}</div>` : ''}
            </div>
            <button type="button" class="cart-item-del" data-action="del" aria-label="移除品項">✕</button>
          </div>
          <div class="cart-item-price-row">
            <span class="cart-item-price">NT$ ${subtotal}</span>
            <div class="cart-qty-ctrl">
              <button type="button" class="cart-qty-btn" data-action="minus" aria-label="減少數量">-</button>
              <span class="cart-qty-val">${qty}</span>
              <button type="button" class="cart-qty-btn" data-action="plus" aria-label="增加數量">+</button>
            </div>
          </div>
        </div>
      </div>
    `;
    }).join('');

    // 綁定加減與刪除事件
    listEl.querySelectorAll('.cart-item-card').forEach(card => {
      const id = card.dataset.id;
      card.querySelector('[data-action="minus"]').addEventListener('click', () => CartStore.updateQty(id, -1));
      card.querySelector('[data-action="plus"]').addEventListener('click', () => CartStore.updateQty(id, 1));
      card.querySelector('[data-action="del"]').addEventListener('click', () => CartStore.remove(id));
    });
  }

  // 監聽更新事件
  window.addEventListener('cart:updated', renderUI);

  // 全域暴露 API
  window.ModernOilCart = {
    add: (prod, qty) => CartStore.add(prod, qty),
    remove: (id) => CartStore.remove(id),
    updateQty: (id, delta) => CartStore.updateQty(id, delta),
    clear: () => CartStore.clear(),
    open: openDrawer,
    close: closeDrawer,
    getItems: () => CartStore.get(),
    getCount: () => CartStore.count(),
    getTotal: () => CartStore.total()
  };

  // 全域監聽「加入購物車」按鈕點擊：任何帶有 data-cart-item 屬性的按鈕
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-add-cart]');
    if (!btn) return;
    e.preventDefault();
    try {
      const dataStr = btn.getAttribute('data-cart-item');
      if (dataStr) {
        const prod = JSON.parse(dataStr);
        CartStore.add(prod, 1);
      }
    } catch (err) {
      console.error('[Cart] 解析商品資訊失敗', err);
    }
  });

  // DOM 載入後初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUI);
  } else {
    initUI();
  }
})();