(() => {
  const form = document.getElementById('booking-form');
  const submitBtn = document.getElementById('booking-submit-btn');
  const confirmBox = document.getElementById('booking-confirm');
  const drawCodeNote = document.getElementById('draw-code-note');
  const formMsg = document.getElementById('booking-form-msg');
  const bookingDateInput = document.getElementById('f-date');

  function escapeHtml(s) {
    return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function localDateString(){
    const now = new Date();
    const offset = now.getTimezoneOffset() * 60000;
    return new Date(now.getTime() - offset).toISOString().slice(0, 10);
  }

  bookingDateInput.min = localDateString();

  const params = new URLSearchParams(window.location.search);
  const drawCode = params.get('code');
  if (drawCode) {
    drawCodeNote.style.display = 'block';
    drawCodeNote.textContent = `已帶入你的抽牌體驗碼：${drawCode}`;
  }

  const concernParam = params.get('concern');
  if (concernParam && document.getElementById('f-concern')) {
    document.getElementById('f-concern').value = concernParam;
  }
  const noteParam = params.get('note');
  if (noteParam && document.getElementById('f-note')) {
    document.getElementById('f-note').value = noteParam;
  }

  // 日式調息逸品奉呈卡 (Cart Summary Banner)
  const cartBanner = document.getElementById('cart-summary-banner');
  const cartCountEl = document.getElementById('csb-item-count');
  const cartListEl = document.getElementById('csb-items-list');
  const cartTotalEl = document.getElementById('csb-total-amount');

  function initCartSummary() {
    let cartItems = [];
    try {
      const raw = localStorage.getItem('modern_oil_cart');
      if (raw) {
        cartItems = JSON.parse(raw);
      }
    } catch (e) {
      console.warn('[Booking] 解析購物車暫存失敗', e);
    }

    if (cartBanner && cartItems && cartItems.length > 0) {
      const count = cartItems.reduce((sum, i) => sum + (i.qty || 1), 0);
      const total = cartItems.reduce((sum, i) => sum + ((i.price || 0) * (i.qty || 1)), 0);

      if (cartCountEl) cartCountEl.textContent = `${count} 件逸品`;
      if (cartTotalEl) cartTotalEl.textContent = `NT$ ${total.toLocaleString()}`;

      if (cartListEl) {
        cartListEl.innerHTML = cartItems.map(item => `
          <div class="csb-item">
            <div style="display:flex;align-items:center;gap:10px;">
              <img src="${escapeHtml(item.image || 'images/logo-emblem.png')}" alt="${escapeHtml(item.name || '')}" class="csb-item-img">
              <div>
                <div class="csb-item-name">${escapeHtml(item.name || '')}</div>
                <div class="csb-item-meta">${item.capacity ? escapeHtml(item.capacity) + ' · ' : ''}數量：${item.qty || 1}</div>
              </div>
            </div>
            <div class="csb-item-price">NT$ ${((item.price || 0) * (item.qty || 1)).toLocaleString()}</div>
          </div>
        `).join('');
      }

      cartBanner.style.display = 'block';

      const noteInput = document.getElementById('f-note');
      if (noteInput && !noteInput.value) {
        const itemNames = cartItems.map(i => `${i.name}×${i.qty || 1}`).join('、');
        noteInput.value = `選購商品：${itemNames} (預約調息合計 NT$ ${total.toLocaleString()})`;
      }
      const concernInput = document.getElementById('f-concern');
      if (concernInput && !concernInput.value) {
        concernInput.value = '購買調息禮盒與專屬體驗';
      }
    }
  }

  initCartSummary();

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    formMsg.textContent = '';

    const fd = new FormData(form);
    const fields = {
      drawCode: drawCode || null,
      name: (fd.get('name') || '').toString().trim(),
      email: (fd.get('email') || '').toString().trim(),
      lineId: (fd.get('lineId') || '').toString().trim(),
      bookingDate: (fd.get('bookingDate') || '').toString() || null,
      mainConcern: (fd.get('mainConcern') || '').toString().trim(),
      mood: (fd.get('mood') || '').toString().trim(),
      question: (fd.get('question') || '').toString().trim(),
      note: (fd.get('note') || '').toString().trim(),
    };

    if (!fields.name) {
      formMsg.textContent = '請填寫姓名。';
      document.getElementById('f-name').focus();
      return;
    }
    if (!fields.email && !fields.lineId) {
      formMsg.textContent = '請至少填寫 Email 或 LINE ID 其中一項。';
      document.getElementById('f-email').focus();
      return;
    }
    if (fields.bookingDate && fields.bookingDate < localDateString()) {
      formMsg.textContent = '預約日期不能早於今天。';
      bookingDateInput.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = '送出中……';

    const submit = (window.OracleSupabase && window.OracleSupabase.createBooking)
      ? window.OracleSupabase.createBooking(fields)
      : Promise.resolve({ receiptNo: null, persisted: false, error: 'Supabase 尚未載入' });

    submit.then(({ receiptNo, persisted, error }) => {
      function escapeHtml(s) {
        return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
      }

      form.style.display = 'none';
      confirmBox.style.display = 'block';
      if (persisted && receiptNo) {
        try {
          localStorage.removeItem('modern_oil_cart');
          if (cartBanner) cartBanner.style.display = 'none';
        } catch (e) {}

        confirmBox.innerHTML = `
          <div class="ep-label">預約已送出，妳的受付編號</div>
          <div class="ep-code">${escapeHtml(receiptNo)}</div>
          <div class="ep-desc">請保留此編號，我們將依約定時間與你聯繫。</div>
          <div id="ai-confirm-msg" class="ai-confirm-msg">正在為你準備一段專屬的前導訊息……</div>
          <a class="home-cta primary" href="index.html">返回首頁</a>`;
        fetchAiConfirmation(receiptNo);
      } else {
        const safeError = escapeHtml(error || '');
        confirmBox.innerHTML = `
          <div class="ep-label">預約尚未成功送出</div>
          <div class="ep-desc">後端保存服務尚未完成設定${safeError ? '（' + safeError + '）' : ''}，請直接透過 LINE 官方帳號與我們聯繫，或稍後再試一次。</div>
          <button type="button" class="home-cta secondary" id="booking-retry-btn">重新填寫</button>`;
        const retryBtn = document.getElementById('booking-retry-btn');
        if (retryBtn) retryBtn.addEventListener('click', () => {
          confirmBox.style.display = 'none';
          form.style.display = 'flex';
          submitBtn.disabled = false;
          submitBtn.textContent = '送出預約';
        });
      }
    });
  });

  // LOG4：呼叫 Supabase Edge Function，用 AI 生成客製化的預約前導訊息
  async function fetchAiConfirmation(receiptNo){
    const msgEl = document.getElementById('ai-confirm-msg');
    if (!msgEl) return;
    const baseUrl = window.OracleSupabase && window.OracleSupabase.SUPABASE_URL;
    if (!baseUrl) { msgEl.style.display = 'none'; return; }

    try {
      const anonKey = window.OracleSupabase && window.OracleSupabase.SUPABASE_ANON_KEY;
      const res = await fetch(`${baseUrl}/functions/v1/generate-booking-confirmation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${anonKey}` },
        body: JSON.stringify({ receiptNo }),
      });
      const data = await res.json();
      if (data.ok && data.message) {
        msgEl.textContent = data.message;
      } else {
        msgEl.style.display = 'none';
      }
    } catch (e) {
      msgEl.style.display = 'none';
    }
  }
})();
