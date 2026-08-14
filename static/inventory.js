(() => {
  const loginWrap = document.getElementById('admin-login-wrap');
  const dashboard = document.getElementById('inventory-dashboard');
  const loginMsg = document.getElementById('admin-login-msg');
  const adminMsg = document.getElementById('admin-msg');
  const invList = document.getElementById('inventory-list');
  const statItems = document.getElementById('stat-items');
  const statExpiring = document.getElementById('stat-expiring');
  const searchInput = document.getElementById('inv-search');
  const addBtn = document.getElementById('inv-add-btn');
  const formWrap = document.getElementById('inv-form-wrap');
  const saveBtn = document.getElementById('inv-save-btn');
  const cancelBtn = document.getElementById('inv-cancel-btn');

  const fName = document.getElementById('inv-f-name');
  const fQty = document.getElementById('inv-f-qty');
  const fInUse = document.getElementById('inv-f-inuse');
  const fUnit = document.getElementById('inv-f-unit');
  const fCapacity = document.getElementById('inv-f-capacity');
  const fExpiry = document.getElementById('inv-f-expiry');
  const fNote = document.getElementById('inv-f-note');

  const client = (window.OracleSupabase && window.OracleSupabase.getClient) ? window.OracleSupabase.getClient() : null;
  if (!client) {
    loginMsg.textContent = 'Supabase 尚未設定完成，無法使用庫存管理。';
    document.getElementById('admin-login-btn').disabled = true;
  }

  let allItems = [];
  let editingId = null;

  function daysUntil(dateStr){
    if (!dateStr) return null;
    const diff = (new Date(dateStr) - new Date());
    return Math.floor(diff / (1000 * 60 * 60 * 24));
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
    const { data, error } = await client.from('oil_inventory').select('*').order('oil_name', { ascending: true });
    if (error) { adminMsg.textContent = '讀取庫存資料失敗：' + error.message; return; }
    allItems = data || [];
    statItems.textContent = allItems.length;
    statExpiring.textContent = allItems.filter(i => {
      const d = daysUntil(i.expiry_date);
      return d !== null && d <= 60;
    }).length;
    adminMsg.textContent = '';
    renderList();
  }

  function renderList(){
    const kw = (searchInput.value || '').trim().toLowerCase();
    const filtered = allItems.filter(i => !kw || (i.oil_name || '').toLowerCase().includes(kw));

    if (!filtered.length) {
      invList.innerHTML = '<div class="admin-msg">沒有符合條件的庫存品項</div>';
      return;
    }

    invList.innerHTML = filtered.map(i => {
      const d = daysUntil(i.expiry_date);
      let badge = '';
      if (d !== null) {
        if (d < 0) badge = '<span class="status-badge status-cancelled">已過期</span>';
        else if (d <= 60) badge = `<span class="status-badge status-pending">${d} 天後到期</span>`;
        else badge = '<span class="status-badge status-done">效期正常</span>';
      }
      return `
        <div class="booking-card">
          <div class="booking-card-head">
            <div class="booking-receipt">${i.oil_name}</div>
            ${badge}
          </div>
          <div class="booking-row">庫存 ${i.quantity} ${i.unit || '瓶'}｜使用中 ${i.in_use || 0} ${i.unit || '瓶'}${i.capacity ? '｜容量 ' + i.capacity : ''}</div>
          ${i.expiry_date ? `<div class="booking-row">有效期限：${i.expiry_date}</div>` : ''}
          ${i.note ? `<div class="booking-row">備註：${i.note}</div>` : ''}
          <div class="booking-actions">
            <button type="button" class="draw-toggle-btn" data-edit="${i.id}">編輯</button>
            <button type="button" class="draw-toggle-btn" data-delete="${i.id}">刪除</button>
          </div>
        </div>`;
    }).join('');

    invList.querySelectorAll('[data-edit]').forEach(btn => {
      btn.addEventListener('click', () => openForm(allItems.find(i => i.id === btn.dataset.edit)));
    });
    invList.querySelectorAll('[data-delete]').forEach(btn => {
      btn.addEventListener('click', () => deleteItem(btn.dataset.delete));
    });
  }

  function openForm(item){
    editingId = item ? item.id : null;
    fName.value = item ? item.oil_name : '';
    fQty.value = item ? item.quantity : '';
    fInUse.value = item ? item.in_use : '';
    fUnit.value = item ? (item.unit || '瓶') : '瓶';
    fCapacity.value = item ? (item.capacity || '') : '';
    fExpiry.value = item ? (item.expiry_date || '') : '';
    fNote.value = item ? (item.note || '') : '';
    formWrap.style.display = 'flex';
  }

  addBtn.addEventListener('click', () => openForm(null));
  cancelBtn.addEventListener('click', () => { formWrap.style.display = 'none'; });

  const syncBtn = document.getElementById('inv-sync-btn');
  syncBtn.addEventListener('click', async () => {
    const baseUrl = window.OracleSupabase && window.OracleSupabase.SUPABASE_URL;
    if (!baseUrl) { adminMsg.textContent = 'Supabase 尚未設定，無法同步。'; return; }
    syncBtn.disabled = true;
    adminMsg.textContent = '正在從 Google 試算表同步……';
    try {
      const res = await fetch(`${baseUrl}/functions/v1/sync-inventory`, { method: 'POST' });
      const data = await res.json();
      if (data.ok) {
        adminMsg.textContent = `同步完成：新增 ${data.inserted} 筆、更新 ${data.updated} 筆`;
        await loadData();
      } else {
        adminMsg.textContent = '同步失敗：' + data.error;
      }
    } catch (e) {
      adminMsg.textContent = '同步失敗：' + e.message;
    }
    syncBtn.disabled = false;
  });

  saveBtn.addEventListener('click', async () => {
    const payload = {
      oil_name: fName.value.trim(),
      quantity: Number(fQty.value) || 0,
      in_use: Number(fInUse.value) || 0,
      unit: fUnit.value.trim() || '瓶',
      capacity: fCapacity.value.trim() || null,
      expiry_date: fExpiry.value || null,
      note: fNote.value.trim() || null,
    };
    if (!payload.oil_name) return;

    const query = editingId
      ? client.from('oil_inventory').update(payload).eq('id', editingId)
      : client.from('oil_inventory').insert(payload);

    const { error } = await query;
    if (error) { adminMsg.textContent = '儲存失敗：' + error.message; return; }
    formWrap.style.display = 'none';
    await loadData();
  });

  async function deleteItem(id){
    if (!confirm('確定要刪除這個品項嗎？')) return;
    const { error } = await client.from('oil_inventory').delete().eq('id', id);
    if (error) { adminMsg.textContent = '刪除失敗：' + error.message; return; }
    await loadData();
  }

  document.getElementById('admin-login-btn').addEventListener('click', async () => {
    const email = document.getElementById('a-email').value.trim();
    const password = document.getElementById('a-pass').value;
    if (!email || !password) return;
    loginMsg.textContent = '登入中……';
    const { error } = await client.auth.signInWithPassword({ email, password });
    if (error) { loginMsg.textContent = '登入失敗：' + error.message; return; }
    const ok = await checkAdminAndEnter();
    if (ok) { loginMsg.textContent = ''; enterDashboard(); }
  });

  searchInput.addEventListener('input', renderList);

  (async () => {
    if (!client) return;
    const { data: { session } } = await client.auth.getSession();
    if (session) {
      const ok = await checkAdminAndEnter();
      if (ok) enterDashboard();
    }
  })();
})();
