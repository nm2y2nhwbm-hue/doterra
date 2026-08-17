(() => {
  const form = document.getElementById('booking-form');
  const submitBtn = document.getElementById('booking-submit-btn');
  const confirmBox = document.getElementById('booking-confirm');
  const drawCodeNote = document.getElementById('draw-code-note');

  const params = new URLSearchParams(window.location.search);
  const drawCode = params.get('code');
  if (drawCode) {
    drawCodeNote.style.display = 'block';
    drawCodeNote.textContent = `已帶入你的抽牌體驗碼：${drawCode}`;
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = '送出中……';

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
      submitBtn.disabled = false;
      submitBtn.textContent = '送出預約';
      return;
    }

    const submit = (window.OracleSupabase && window.OracleSupabase.createBooking)
      ? window.OracleSupabase.createBooking(fields)
      : Promise.resolve({ receiptNo: null, persisted: false, error: 'Supabase 尚未載入' });

    submit.then(({ receiptNo, persisted, error }) => {
      form.style.display = 'none';
      confirmBox.style.display = 'block';
      if (persisted && receiptNo) {
        confirmBox.innerHTML = `
          <div class="ep-label">預約已送出，妳的受付編號</div>
          <div class="ep-code">${receiptNo}</div>
          <div class="ep-desc">請保留此編號，我們將依約定時間與你聯繫。</div>
          <div id="ai-confirm-msg" class="ai-confirm-msg">正在為你準備一段專屬的前導訊息……</div>
          <a class="home-cta primary" href="index.html">返回首頁</a>`;
        fetchAiConfirmation(receiptNo);
      } else {
        confirmBox.innerHTML = `
          <div class="ep-label">預約尚未成功送出</div>
          <div class="ep-desc">後端保存服務尚未完成設定${error ? '（' + error + '）' : ''}，請直接透過 LINE 官方帳號與我們聯繫，或稍後再試一次。</div>
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
