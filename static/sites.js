(() => {
  const loginWrap = document.getElementById('admin-login-wrap');
  const dashboard = document.getElementById('sites-dashboard');
  const loginMsg = document.getElementById('admin-login-msg');
  const sitesMsg = document.getElementById('sites-msg');
  const vendorList = document.getElementById('vendor-status-list');
  const projectList = document.getElementById('project-status-list');
  const refreshBtn = document.getElementById('refresh-btn');

  const client = (window.OracleSupabase && window.OracleSupabase.getClient) ? window.OracleSupabase.getClient() : null;
  if (!client) {
    loginMsg.textContent = 'Supabase 尚未設定完成，無法使用網站管理中心。';
    document.getElementById('admin-login-btn').disabled = true;
  }

  // ---------------------------------------------------------
  // Production URLs / GitHub repository
  // ---------------------------------------------------------
  const SITE_URL = 'https://doterra-two.vercel.app/booking.html';
  const BACKEND_PING_URL = 'https://doterra-73pv.onrender.com/api/oils';
  const GITHUB_OWNER = 'nm2y2nhwbm-hue';
  const GITHUB_REPO = 'doterra';
  const GITHUB_BRANCH = 'main';

  const VENDORS = [
    { key: 'github',   name: 'GitHub',   api: 'https://www.githubstatus.com/api/v2/status.json', page: 'https://www.githubstatus.com', note: 'Git 倉庫／Actions 部署工作流' },
    { key: 'vercel',   name: 'Vercel',   api: 'https://www.vercel-status.com/api/v2/status.json', page: 'https://www.vercel-status.com', note: '前端網頁託管／邊緣網路' },
    { key: 'render',   name: 'Render',   api: 'https://status.render.com/api/v2/status.json', page: 'https://status.render.com', note: '後端 Web 服務／排程執行器' },
    { key: 'supabase', name: 'Supabase', api: 'https://status.supabase.com/api/v2/status.json', page: 'https://status.supabase.com', note: 'PostgreSQL 資料庫／Auth 驗證機房' },
    { key: 'line',     name: 'LINE Developers', api: 'https://api.line-status.info/api/v2/status.json', page: 'https://api.line-status.info/', note: 'Messaging API／LINE Developers／LIFF／LINE Login' },
  ];

  function statusBadgeHtml(level, text){
    const cls = level === 'ok' ? 'status-done' : level === 'warn' ? 'status-pending' : level === 'bad' ? 'status-cancelled' : 'status-contacted';
    return `<span class="status-badge ${cls}">${text}</span>`;
  }

  function fetchWithTimeout(url, opts = {}, timeoutMs = 6000){
    return Promise.race([
      fetch(url, opts),
      new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), timeoutMs)),
    ]);
  }

  async function checkVendor(v){
    const start = performance.now();
    if (!v.api) {
      return { ...v, level: 'unknown', label: '無公開 API', detail: '僅能人工查看官網' };
    }
    try {
      const res = await fetchWithTimeout(v.api, {}, 6000);
      const ms = Math.round(performance.now() - start);
      if (!res.ok) return { ...v, level: 'bad', label: `HTTP ${res.status}`, detail: `${ms}ms` };
      const data = await res.json();
      const indicator = data.status && data.status.indicator;
      const desc = (data.status && data.status.description) || '';
      const level = indicator === 'none' ? 'ok' : (indicator === 'minor' ? 'warn' : 'bad');
      const label = indicator === 'none' ? '正常 (Operational)' : desc || indicator;
      return { ...v, level, label, detail: `${ms}ms` };
    } catch (e) {
      return { ...v, level: 'unknown', label: '無法讀取（可能是 CORS 或連線問題）', detail: String(e.message || e) };
    }
  }

  async function checkFrontend(){
    const start = performance.now();
    try {
      await fetchWithTimeout(SITE_URL, { mode: 'no-cors' }, 6000);
      const ms = Math.round(performance.now() - start);
      return { level: 'ok', label: `回應正常`, detail: `${ms}ms（no-cors 模式，僅能判斷是否連得上）` };
    } catch (e) {
      return { level: 'bad', label: '連線失敗', detail: String(e.message || e) };
    }
  }

  async function checkBackend(){
    const start = performance.now();
    try {
      const res = await fetchWithTimeout(BACKEND_PING_URL, {}, 6000);
      const ms = Math.round(performance.now() - start);
      if (!res.ok) return { level: 'bad', label: `HTTP ${res.status}`, detail: `${ms}ms` };
      return { level: 'ok', label: 'UP', detail: `${ms}ms（用 /api/oils 當存活探測，建議之後加專用 /api/healthz）` };
    } catch (e) {
      return { level: 'bad', label: '請求逾時或失敗', detail: String(e.message || e) };
    }
  }

  async function checkDbHealth(){
    try {
      const { data, error } = await client.rpc('get_db_health');
      if (error) throw error;
      const usedRatio = data.max_connections ? (data.active_connections / data.max_connections) : 0;
      const connLevel = usedRatio > 0.85 ? 'bad' : usedRatio > 0.6 ? 'warn' : 'ok';
      return {
        size: { level: 'ok', label: data.db_size_pretty, detail: '資料庫容量' },
        conn: { level: connLevel, label: `${data.active_connections} / ${data.max_connections}`, detail: '目前連線數' },
      };
    } catch (e) {
      return {
        size: { level: 'unknown', label: '無法讀取', detail: String(e.message || e) },
        conn: { level: 'unknown', label: '無法讀取', detail: '' },
      };
    }
  }

  async function checkGithub(){
    if (GITHUB_OWNER.startsWith('YOUR-') || GITHUB_REPO.startsWith('YOUR-')) {
      return { level: 'unknown', label: '尚未設定 GitHub 資訊', detail: '請在 sites.js 填入 GITHUB_OWNER / GITHUB_REPO' };
    }
    try {
      const res = await fetchWithTimeout(
        `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/commits/${GITHUB_BRANCH}`, {}, 6000
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}（若為私有 repo，公開 API 讀不到，需要另外接 token）`);
      const data = await res.json();
      const sha = (data.sha || '').slice(0, 7);
      const when = data.commit && data.commit.author && data.commit.author.date;
      const msg = data.commit && data.commit.message ? data.commit.message.split('\n')[0] : '';
      return { level: 'ok', label: `${sha} ・ ${msg}`, detail: when ? new Date(when).toLocaleString('zh-TW') : '' };
    } catch (e) {
      return { level: 'unknown', label: '無法讀取', detail: String(e.message || e) };
    }
  }

  function renderRow(container, title, sub, result, linkUrl){
    const el = document.createElement('div');
    el.className = 'booking-card';
    el.innerHTML = `
      <div class="booking-card-head">
        <div>
          <div class="booking-receipt">${title}</div>
          <div class="booking-created">${sub || ''}</div>
        </div>
        ${statusBadgeHtml(result.level, result.label)}
      </div>
      ${result.detail ? `<div class="booking-row">${result.detail}</div>` : ''}
      ${linkUrl ? `<div class="booking-actions"><a class="draw-toggle-btn" href="${linkUrl}" target="_blank" rel="noopener" style="text-decoration:none;display:inline-block;">開啟官方頁面 →</a></div>` : ''}
    `;
    container.appendChild(el);
  }

  async function checkLineWebhook(){
    const start = performance.now();
    try {
      const res = await fetchWithTimeout('https://doterra-73pv.onrender.com/health', {}, 6000);
      const ms = Math.round(performance.now() - start);
      if (!res.ok) return { level: 'bad', label: `HTTP ${res.status}`, detail: `${ms}ms（後端 Webhook 接收端異常）` };
      return { 
        level: 'ok', 
        label: '接收伺服器在線 (Ready)', 
        detail: `回應速度 ${ms}ms · 官方詳細統計與成功率請至 LINE Developers 後台查看` 
      };
    } catch (e) {
      return { level: 'bad', label: '接收端點連線異常', detail: String(e.message || e) };
    }
  }

  async function runAllChecks(){
    sitesMsg.textContent = '檢查中……';
    vendorList.innerHTML = '';
    projectList.innerHTML = '';

    const vendorResults = await Promise.all(VENDORS.map(checkVendor));
    vendorResults.forEach(v => renderRow(vendorList, v.name, v.note, v, v.page));

    const [frontend, backend, dbHealth, github, lineWebhook] = await Promise.all([
      checkFrontend(), checkBackend(), checkDbHealth(), checkGithub(), checkLineWebhook(),
    ]);
    renderRow(projectList, '前端站點響應', '從後台發送請求至正式預約頁', frontend);
    renderRow(projectList, '後端 API 存活', 'Render 服務探測', backend);
    renderRow(projectList, '資料庫容量', 'pg_database_size', dbHealth.size);
    renderRow(projectList, '資料庫連線數', 'pg_stat_activity', dbHealth.conn);
    renderRow(projectList, 'LINE Webhook 接收狀態', 'Render /callback 接收端點探測', lineWebhook, 'https://developers.line.biz/console/');
    renderRow(projectList, '當前生產版本', 'GitHub 最新 Commit', github);

    sitesMsg.textContent = '';
  }

  refreshBtn.addEventListener('click', runAllChecks);

  async function checkAdminAndEnter(){
    const { data: { user } } = await client.auth.getUser();
    if (!user) return false;
    const { data, error } = await client.from('admins').select('user_id').eq('user_id', user.id).maybeSingle();
    if (error || !data) {
      loginMsg.textContent = '此帳號沒有管理權限。';
      await client.auth.signOut();
      return false;
    }
    return true;
  }

  document.getElementById('admin-login-btn').addEventListener('click', async () => {
    const email = document.getElementById('a-email').value.trim();
    const password = document.getElementById('a-pass').value;
    if (!email || !password) return;
    loginMsg.textContent = '登入中……';
    const { error } = await client.auth.signInWithPassword({ email, password });
    if (error) { loginMsg.textContent = '登入失敗：' + error.message; return; }
    const ok = await checkAdminAndEnter();
    if (ok) {
      loginMsg.textContent = '';
      loginWrap.style.display = 'none';
      dashboard.style.display = 'block';
      runAllChecks();
    }
  });

  (async () => {
    if (!client) return;
    const { data: { session } } = await client.auth.getSession();
    if (session) {
      const ok = await checkAdminAndEnter();
      if (ok) {
        loginWrap.style.display = 'none';
        dashboard.style.display = 'block';
        runAllChecks();
      }
    }
  })();
})();
