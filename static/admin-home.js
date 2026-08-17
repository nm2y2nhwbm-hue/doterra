(() => {
  const loginWrap = document.getElementById('admin-login-wrap');
  const dashboard = document.getElementById('admin-dashboard');
  const loginMsg = document.getElementById('admin-login-msg');
  const adminMsg = document.getElementById('admin-msg');
  const statBookings = document.getElementById('stat-bookings');
  const statDraws = document.getElementById('stat-draws');
  const loginBtn = document.getElementById('admin-login-btn');
  const logoutBtn = document.getElementById('admin-logout-btn');

  const client = (window.OracleSupabase && window.OracleSupabase.getClient)
    ? window.OracleSupabase.getClient()
    : null;

  if (!client) {
    loginMsg.textContent = 'Supabase 尚未設定完成，無法使用管理後台。';
    loginBtn.disabled = true;
    return;
  }

  async function hasAdminAccess(){
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

  async function loadStats(){
    adminMsg.textContent = '讀取中……';
    const [bookingRes, drawRes] = await Promise.all([
      client.from('bookings').select('*', { count: 'exact', head: true }),
      client.from('draws').select('*', { count: 'exact', head: true }),
    ]);
    statBookings.textContent = bookingRes.error ? '–' : (bookingRes.count ?? 0);
    statDraws.textContent = drawRes.error ? '–' : (drawRes.count ?? 0);
    adminMsg.textContent = '';
  }

  async function enterDashboard(){
    loginWrap.style.display = 'none';
    dashboard.style.display = 'block';
    await loadStats();
  }

  loginBtn.addEventListener('click', async () => {
    const email = document.getElementById('a-email').value.trim();
    const password = document.getElementById('a-pass').value;
    if (!email || !password) return;
    loginMsg.textContent = '登入中……';
    const { error } = await client.auth.signInWithPassword({ email, password });
    if (error) {
      loginMsg.textContent = '登入失敗：' + error.message;
      return;
    }
    if (await hasAdminAccess()) {
      loginMsg.textContent = '';
      enterDashboard();
    }
  });

  logoutBtn.addEventListener('click', async () => {
    await client.auth.signOut();
    dashboard.style.display = 'none';
    loginWrap.style.display = 'flex';
  });

  (async () => {
    const { data: { session } } = await client.auth.getSession();
    if (session && await hasAdminAccess()) enterDashboard();
  })();
})();