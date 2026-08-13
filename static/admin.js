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

    bookingList.innerHTML = filtered.map(b => `
      <div class="booking-card" data-receipt="${b.receipt_no}">
        <div class="booking-card-head">
          <div>
            <div class="booking-receipt">${b.receipt_no}</div>
            <div class="booking-created">${new Date(b.created_at).toLocaleString('zh-TW')}</div>
          </div>
          <span class="status-badge ${statusClass(b.status)}">${b.status}</span>
        </div>
        <div class="booking-row"><b>${b.name || ''}</b>${b.email ? ' · ' + b.email : ''}${b.line_id ? ' · LINE: ' + b.line_id : ''}</div>
        ${b.main_concern ? `<div class="booking-row">主要困擾：${b.main_concern}</div>` : ''}
        ${b.current_mood ? `<div class="booking-row">當下心情：${b.current_mood}</div>` : ''}
        ${b.booking_date ? `<div class="booking-row">預約日期：${b.booking_date}</div>` : ''}
        ${b.question ? `<div class="booking-row">諮詢問題：${b.question}</div>` : ''}
        ${b.note ? `<div class="booking-row">補充說明：${b.note}</div>` : ''}
        <div class="booking-actions">
          <select class="form-input booking-status-select" data-receipt="${b.receipt_no}">
            <option value="待處理" ${b.status === '待處理' ? 'selected' : ''}>待處理</option>
            <option value="已聯繫" ${b.status === '已聯繫' ? 'selected' : ''}>已聯繫</option>
            <option value="已完成" ${b.status === '已完成' ? 'selected' : ''}>已完成</option>
            <option value="取消" ${b.status === '取消' ? 'selected' : ''}>取消</option>
          </select>
          ${b.draw_code ? `<button type="button" class="draw-toggle-btn" data-code="${b.draw_code}">查看抽牌結果 ▾</button>` : ''}
        </div>
        <div class="draw-detail" id="draw-detail-${b.draw_code || ''}" style="display:none;"></div>
      </div>
    `).join('');

    bookingList.querySelectorAll('.booking-status-select').forEach(sel => {
      sel.addEventListener('change', () => updateStatus(sel.dataset.receipt, sel.value));
    });
    bookingList.querySelectorAll('.draw-toggle-btn').forEach(btn => {
      btn.addEventListener('click', () => toggleDrawDetail(btn.dataset.code));
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
    el.innerHTML = `
      <div class="draw-detail-meta">模式 ${draw.mode}．${new Date(draw.created_at).toLocaleString('zh-TW')}</div>
      <div class="draw-detail-cards">
        ${results.map(r => `
          <div class="draw-detail-card">
            <img src="${r.image_url}" alt="${r.card_name}">
            <div class="ddc-label">${r.label}</div>
            <div class="ddc-name">${r.card_name}</div>
          </div>`).join('')}
      </div>`;
  }

  document.getElementById('module-inventory').querySelector('.amc-link').addEventListener('click', (e) => {
    e.preventDefault();
    alert('精油庫存管理｜敬請期待，近期上線。\n（將整合 Google 試算表同步、庫存與有效期限預警）');
  });
  document.getElementById('module-sites').querySelector('.amc-link').addEventListener('click', (e) => {
    e.preventDefault();
    alert('網站管理中心｜敬請期待，近期上線。\n（將整合 GitHub／LINE Developers／Render／Vercel／Supabase 多站狀態監看）');
  });

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
