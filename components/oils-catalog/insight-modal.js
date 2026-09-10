/**
 * 雫之洞悉 · 返魂堂 · 精油圖鑑自然醫學調息彈窗控制器 (components/oils-catalog/insight-modal.js)
 * 提供 131 款精油圖鑑 Modal、三大位格印章與自然醫學調息箋互動邏輯
 */
(function() {
  'use strict';

  let modalEl = null;
  let lastActiveEl = null;

  function getModal() {
    if (!modalEl) {
      modalEl = document.getElementById('insight-modal');
    }
    return modalEl;
  }

  function open(oil) {
    if (!oil) return;
    const modal = getModal();
    if (!modal) return;

    lastActiveEl = document.activeElement;

    // 填充卡牌圖檔
    const artEl = modal.querySelector('#m-art');
    if (artEl) {
      artEl.src = oil.image_filename ? `images/${oil.image_filename}` : 'images/logo-emblem.png';
      artEl.alt = oil.name || '精油圖鑑卡牌';
      artEl.onerror = () => { artEl.src = 'images/logo-emblem.png'; };
    }

    // 編號與標題
    const skuEl = modal.querySelector('#m-sku');
    if (skuEl) skuEl.textContent = `OFFICIAL SKU: ${oil.sku || '--'}`;

    const nameEl = modal.querySelector('#m-name');
    if (nameEl) nameEl.textContent = oil.name || '--';

    const enEl = modal.querySelector('#m-en');
    if (enEl) enEl.textContent = oil.name_en || '--';

    // 三大位格印章
    const pillarEl = modal.querySelector('#m-pillar');
    if (pillarEl) {
      const pillar = oil.pillar || '中柱 · 平衡';
      pillarEl.textContent = pillar;
      let tagClass = 'tag-balance';
      if (pillar.includes('右柱')) tagClass = 'tag-mercy';
      if (pillar.includes('左柱')) tagClass = 'tag-severity';
      pillarEl.className = `seal-pill ${tagClass}`;
    }

    // 容量規格
    const capEl = modal.querySelector('#m-capacity');
    if (capEl) capEl.textContent = `規格：${oil.capacity || '15ml'}`;

    // 建議售價
    const price = Number(oil.price) || 1310;
    const priceEl = modal.querySelector('#m-price');
    if (priceEl) priceEl.textContent = `建議售價 NT$ ${price.toLocaleString()}`;

    // 用法標籤 (A T I)
    const usageEl = modal.querySelector('#m-usage');
    if (usageEl) usageEl.textContent = oil.usage_tags || 'A T I';

    // 塗抹安全印章
    const safetyEl = modal.querySelector('#m-safety');
    if (safetyEl) {
      const guide = oil.dilution_guide || '直塗';
      if (guide === '敏感') {
        safetyEl.textContent = '⚠️ 敏感膚質稀釋';
        safetyEl.className = 'seal-safety safety-sensitive';
      } else if (guide === '稀釋') {
        safetyEl.textContent = '💧 強效必須稀釋';
        safetyEl.className = 'seal-safety safety-dilute';
      } else {
        safetyEl.textContent = '🌿 溫和可直塗';
        safetyEl.className = 'seal-safety safety-direct';
      }
    }

    // 自然醫學調息指引
    const docEl = modal.querySelector('#m-doctor');
    if (docEl) docEl.textContent = oil.doctor_advice || '主調和身心、平衡能量。';

    // 心靈指引與脈輪
    const guideEl = modal.querySelector('#m-guidance');
    if (guideEl) guideEl.textContent = oil.guidance || oil.description || '靜心體會香氣流動。';

    const chakraEl = modal.querySelector('#m-chakra');
    if (chakraEl) chakraEl.textContent = oil.chakra || '心輪';

    // 加入調息清單按鈕綁定
    const addBtn = modal.querySelector('#m-add-cart-btn');
    if (addBtn) {
      addBtn.innerHTML = `<span>＋ 加入調息清單 (NT$ ${price.toLocaleString()})</span>`;
      addBtn.onclick = () => {
        if (window.ModernOilCart) {
          window.ModernOilCart.add({
            id: oil.sku || oil.name,
            name: oil.name + (oil.name_en ? ` (${oil.name_en})` : ''),
            price: price,
            capacity: oil.capacity || '15ml',
            pillar: oil.pillar || '現代精油',
            image: oil.image_filename ? `images/${oil.image_filename}` : 'images/logo-emblem.png'
          }, 1);
        }
      };
    }

    // 開啟彈窗並防止背景捲動
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // 聚焦關閉按鈕提升無障礙體驗
    const closeBtn = modal.querySelector('#insight-close-btn');
    if (closeBtn) closeBtn.focus();
  }

  function close() {
    const modal = getModal();
    if (!modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastActiveEl && typeof lastActiveEl.focus === 'function') {
      lastActiveEl.focus();
    }
  }

  function init() {
    const modal = getModal();
    if (!modal) return;

    // 點擊背景關閉
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        close();
      }
    });

    // 關閉按鈕
    const closeBtn = modal.querySelector('#insight-close-btn');
    if (closeBtn) {
      closeBtn.addEventListener('click', close);
    }

    // 鍵盤 Escape 鍵
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal.classList.contains('active')) {
        close();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.ModernOilInsightModal = {
    open: open,
    close: close
  };
})();
