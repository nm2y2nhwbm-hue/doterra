(() => {
  const loginWrap = document.getElementById('admin-login-wrap');
  const dashboard = document.getElementById('admin-dashboard');
  const loginMsg = document.getElementById('admin-login-msg');
  const adminMsg = document.getElementById('admin-msg');
  const bookingList = document.getElementById('booking-list');
  const statBookings = document.getElementById('stat-bookings');
  const statDraws = document.getElementById('stat-draws');
  const searchInput = document.getElementById('admin-search');
  const statusFilter = document.getElementById('admin-status-filter');
  const resetBtn = document.getElementById('admin-reset-btn');

  const client = (window.OracleSupabase && window.OracleSupabase.getClient) ? window.OracleSupabase.getClient() : null;

  if (!client) {
    loginMsg.textContent = 'Supabase 尚未設定完成，無法使用管理後台。';
    document.getElementById('admin-login-btn').disabled = true;
  }

  let allBookings = [];
  const drawCache = {};

  function statusClass(status){
    if (status === '已完成') return 'status-done';
    if (status === '已聯繫') return 'status-contacted';
    if (status === '取消') return 'status-cancelled';
    return 'status-pending';
  }

  async function checkAdminAndEnter(){
    const { data: { user } } = await client.auth.getUser();
    if (!user) return false;
    const { data, error } = await client.from('admins').select('user_id').eq('user_id', user.id).maybeSingle();
    if (error || !data) {
      adminMsg.textContent = '此帳號沒有管理權限，請聯絡系統管理員將你的帳號加入白名單。';
      await client.auth.signOut();
      return false;
    }
    return true;
  }

  async function enterDashboard(){
    loginWrap.style.display = 'none';
    dashboard.style.display = 'block';
    await loadData();
  }

  async function loadData(){
    adminMsg.textContent = '讀取中……';
    const [{ data: bookings, error: bErr }, { count: drawCount, error: dErr }] = await Promise.all([
      client.from('bookings').select('*').order('created_at', { ascending: false }),
      client.from('draws').select('*', { count: 'exact', head: true }),
    ]);
    if (bErr) { adminMsg.textContent = '讀取預約資料失敗：' + bErr.message; return; }
    allBookings = bookings || [];
    statBookings.textContent = allBookings.length;
    statDraws.textContent = dErr ? '–' : (drawCount ?? 0);
    adminMsg.textContent = '';
    renderList();
  }

  function escapeHtml(str){
    if (str == null) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function sanitizeUrl(url){
    if (!url) return '';
    const clean = String(url).trim();
    if (/^(https?:\/\/|\/|images\/)/i.test(clean)) {
      return clean.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }
    return '';
  }

  function renderList(){
    const kw = (searchInput.value || '').trim().toLowerCase();
    const statusWanted = statusFilter.value;
    const filtered = allBookings.filter(b => {
      if (statusWanted && b.status !== statusWanted) return false;
      if (!kw) return true;
      return [b.receipt_no, b.name, b.line_id, b.email].some(v => (v || '').toLowerCase().includes(kw));
    });

    if (!filtered.length) {
      bookingList.innerHTML = '<div class="admin-msg">沒有符合條件的預約紀錄</div>';
      return;
    }

    bookingList.innerHTML = filtered.map(b => {
      const receipt = escapeHtml(b.receipt_no);
      const name = escapeHtml(b.name || '');
      const email = escapeHtml(b.email || '');
      const lineId = escapeHtml(b.line_id || '');
      const status = escapeHtml(b.status || '');
      const mainConcern = escapeHtml(b.main_concern || '');
      const currentMood = escapeHtml(b.current_mood || '');
      const bookingDate = escapeHtml(b.booking_date || '');
      const question = escapeHtml(b.question || '');
      const note = escapeHtml(b.note || '');
      const drawCode = escapeHtml(b.draw_code || '');
      const createdAt = escapeHtml(new Date(b.created_at).toLocaleString('zh-TW'));

      return `
      <div class="booking-card" data-receipt="${receipt}">
        <div class="booking-card-head">
          <div>
            <div class="booking-receipt">${receipt}</div>
            <div class="booking-created">${createdAt}</div>
          </div>
          <span class="status-badge ${statusClass(b.status)}">${status}</span>
        </div>
        <div class="booking-row"><b>${name}</b>${email ? ' · ' + email : ''}${lineId ? ' · LINE: ' + lineId : ''}</div>
        ${mainConcern ? `<div class="booking-row">主要困擾：${mainConcern}</div>` : ''}
        ${currentMood ? `<div class="booking-row">當下心情：${currentMood}</div>` : ''}
        ${bookingDate ? `<div class="booking-row">預約日期：${bookingDate}</div>` : ''}
        ${question ? `<div class="booking-row">諮詢問題：${question}</div>` : ''}
        ${note ? `<div class="booking-row">補充說明：${note}</div>` : ''}
        <div class="booking-actions">
          <select class="form-input booking-status-select" data-receipt="${receipt}">
            <option value="待處理" ${b.status === '待處理' ? 'selected' : ''}>待處理</option>
            <option value="已聯繫" ${b.status === '已聯繫' ? 'selected' : ''}>已聯繫</option>
            <option value="已完成" ${b.status === '已完成' ? 'selected' : ''}>已完成</option>
            <option value="取消" ${b.status === '取消' ? 'selected' : ''}>取消</option>
          </select>
          ${drawCode ? `<button type="button" class="draw-toggle-btn" data-code="${drawCode}">查看抽牌結果 ▾</button>` : ''}
          <button type="button" class="danger-action-btn delete-booking-btn" data-delete-receipt="${receipt}">刪除預約</button>
        </div>
        <div class="draw-detail" id="draw-detail-${drawCode}" style="display:none;"></div>
      </div>
    `;
    }).join('');

    bookingList.querySelectorAll('.booking-status-select').forEach(sel => {
      sel.addEventListener('change', () => updateStatus(sel.dataset.receipt, sel.value));
    });
    bookingList.querySelectorAll('.draw-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => toggleDrawDetail(btn.dataset.code));
    });
    bookingList.querySelectorAll('[data-delete-receipt]').forEach(btn => {
      btn.addEventListener('click', () => deleteBooking(btn.dataset.deleteReceipt, btn));
    });
  }

  async function updateStatus(receiptNo, status){
    const { error } = await client.from('bookings').update({ status }).eq('receipt_no', receiptNo);
    const b = allBookings.find(x => x.receipt_no === receiptNo);
    if (error) {
      adminMsg.textContent = '更新狀態失敗：' + error.message;
      return;
    }
    if (b) b.status = status;
    renderList();
  }

  async function deleteBooking(receiptNo, button){
    const booking = allBookings.find(x => x.receipt_no === receiptNo);
    const linkedNote = booking && booking.draw_code
      ? '\n\n對應抽牌紀錄會保留；只有「全部歸零」才會一併清除抽牌紀錄。'
      : '';
    if (!confirm(`確定刪除受付編號 ${receiptNo} 的預約嗎？${linkedNote}`)) return;

    button.disabled = true;
    adminMsg.textContent = '刪除中……';
    const { data, error } = await client
      .from('bookings')
      .delete()
      .eq('receipt_no', receiptNo)
      .select('receipt_no')
      .maybeSingle();

    if (error || !data) {
      button.disabled = false;
      adminMsg.textContent = '刪除失敗：' + (error ? error.message : '沒有刪除權限或紀錄已不存在');
      return;
    }

    allBookings = allBookings.filter(x => x.receipt_no !== receiptNo);
    statBookings.textContent = allBookings.length;
    adminMsg.textContent = `已刪除 ${receiptNo}；對應抽牌紀錄仍保留。`;
    renderList();
  }

  async function resetReception(){
    const phrase = prompt('此操作會永久清除全部預約、抽牌紀錄與受付編號計數器。\n\n請輸入「全部歸零」繼續：');
    if (phrase === null) return;
    if (phrase.trim() !== '全部歸零') {
      adminMsg.textContent = '確認文字不正確，沒有刪除任何資料。';
      return;
    }
    if (!confirm('最後確認：全部預約、抽牌紀錄及受付編號計數器都會歸零，且無法復原。確定繼續？')) return;

    resetBtn.disabled = true;
    adminMsg.textContent = '全部歸零中……';
    const { data, error } = await client.rpc('admin_reset_reception');
    resetBtn.disabled = false;

    if (error) {
      adminMsg.textContent = '全部歸零失敗：' + error.message;
      return;
    }

    allBookings = [];
    Object.keys(drawCache).forEach(key => delete drawCache[key]);
    statBookings.textContent = '0';
    statDraws.textContent = '0';
    renderList();
    const removedBookings = data && Number.isFinite(Number(data.bookings)) ? Number(data.bookings) : 0;
    const removedDraws = data && Number.isFinite(Number(data.draws)) ? Number(data.draws) : 0;
    adminMsg.textContent = `歸零完成：刪除 ${removedBookings} 筆預約、${removedDraws} 筆抽牌紀錄。`;
  }

  async function toggleDrawDetail(code){
    const el = document.getElementById(`draw-detail-${code}`);
    if (!el) return;
    const isOpen = el.style.display !== 'none';
    if (isOpen) { el.style.display = 'none'; return; }

    if (!drawCache[code]) {
      el.style.display = 'block';
      el.innerHTML = '<div class="admin-msg">讀取中……</div>';
      const { data, error } = await client.from('draws').select('*').eq('code', code).maybeSingle();
      if (error || !data) {
        el.innerHTML = '<div class="admin-msg">找不到對應的抽牌紀錄</div>';
        return;
      }
      drawCache[code] = data;
    }

    const draw = drawCache[code];
    const results = Array.isArray(draw.results) ? draw.results : [];
    el.style.display = 'block';
    const mode = escapeHtml(draw.mode || '');
    const createdAt = escapeHtml(new Date(draw.created_at).toLocaleString('zh-TW'));
    el.innerHTML = `
      <div class="draw-detail-meta">模式 ${mode}．${createdAt}</div>
      <div class="draw-detail-cards">
        ${results.map(r => `
          <div class="draw-detail-card">
            <img src="${sanitizeUrl(r.image_url)}" alt="${escapeHtml(r.card_name)}">
            <div class="ddc-label">${escapeHtml(r.label)}</div>
            <div class="ddc-name">${escapeHtml(r.card_name)}</div>
          </div>`).join('')}
      </div>`;
  }

  document.getElementById('admin-login-btn').addEventListener('click', async () => {
    const email = document.getElementById('a-email').value.trim();
    const password = document.getElementById('a-pass').value;
    if (!email || !password) return;
    loginMsg.textContent = '登入中……';
    const { error } = await client.auth.signInWithPassword({ email, password });
    if (error) {
      loginMsg.textContent = '登入失敗：' + error.message;
      return;
    }
    const ok = await checkAdminAndEnter();
    if (ok) {
      loginMsg.textContent = '';
      enterDashboard();
    }
  });

  document.getElementById('admin-logout-btn').addEventListener('click', async () => {
    await client.auth.signOut();
    dashboard.style.display = 'none';
    loginWrap.style.display = 'flex';
  });

  searchInput.addEventListener('input', renderList);
  statusFilter.addEventListener('change', renderList);
  resetBtn.addEventListener('click', resetReception);

  // 若已經有有效登入狀態（例如重新整理頁面），直接進後台
  (async () => {
    if (!client) return;
    const { data: { session } } = await client.auth.getSession();
    if (session) {
      const ok = await checkAdminAndEnter();
      if (ok) enterDashboard();
    }
  })();
})();
