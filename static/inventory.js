(() => {
  const loginWrap = document.getElementById('admin-login-wrap');
  const dashboard = document.getElementById('inventory-dashboard');
  const loginMsg = document.getElementById('admin-login-msg');
  const adminMsg = document.getElementById('admin-msg');
  const invList = document.getElementById('inventory-list');
  let knowledgeMap = new Map();
  fetch('oils-knowledge.json').then(r => r.json()).then(arr => {
    arr.forEach(k => {
      if (k.name) knowledgeMap.set(k.name, k);
      if (k.sku) knowledgeMap.set(k.sku, k);
    });
    if (typeof items !== 'undefined' && items && items.length) renderList();
  }).catch(() => {});
  // 來源：dōTERRA 官方「單方精油速查表」產品編號（最新版價目表）
  const SINGLE_OIL_IDS = new Set([
    '49360302','60227966','30790302','60226389','60228183','60210282','60204088','49350302',
    '60215216','49300302','41850302','60227967','30420302','30040302','60202988','30780302',
    '60212104','31590302','60222082','30070302','41290302','30090302','60215600','30100302',
    '60208195','60223607','30410302','30110302','49290302','60226277','30130302','60210281',
    '30870302','60201178','60219116','60201179','30140302','30850302','30160302','30180302',
    '30890302','30190302','60201071','60208152','30800302','60200025','30200302','30210302',
    '41860302','60203437','60222515','60201067','31610402','30150302','60223050','60228181',
    '30430302','30170302','31620302','60229920','30240302',
  ]);
  // 來源：dōTERRA 官方「複方精油速查表」+ 芳香調理心情套裝 + 呵護系列 Touch 產品編號
  const BLEND_OIL_IDS = new Set([
    '60210284','31200302','31010302','60200200','60220828','60201689','60204858','60209002',
    '60208815','31050302','60228182','60201621','60219115','60224972','60224971','60220683',
    '60224341','60210808','60218546','31060302','60220846','60216131','31460302',
    '60220872','31730302','31750302','60220855','60220862','31710302',
    '60201168','60210814','60202986','60201171','60202979','60201183','60201167','60202980',
    '60201173','60222041','60214452','60205727','60201166','60214477','60223652','60224090',
    '60210809','60215029',
  ]);
  // 名稱關鍵字當備援（沒有產品編號，或編號沒對到清單時才用）
  const SINGLE_OIL_KEYWORDS = [
    '羅勒','肉桂','丁香','乳香','天竺葵','葡萄柚','薰衣草','檸檬草','檸檬','馬鬱蘭','茶樹','沒藥',
    '野橘','牛至','薄荷','迷迭香','檀香','百里香','伊蘭','永久花','快樂鼠尾草','岩蘭草','胡荽','佛手柑',
    '洋甘菊','香蜂草','萊姆','廣藿香','尤加利','冷杉','綠薄荷','冬青','黑胡椒','茴香','雪松',
    '豆蔻','側柏','玫瑰','穗甘松','苦橙葉','橙花','茉莉','山雞椒','麥蘆卡','古巴香脂','藍艾菊','蓍草',
    '薑黃','粉紅胡椒','青橘','黑雲杉','絲柏','桂皮','生薑','香草','鼠尾草','癒創木','樺樹','艾草',
  ];
  const BLEND_OIL_KEYWORDS = [
    '安定平衡','柑橘清新','樂活','舒緩','淨化清新','芳香調理','元氣煥能','元氣','天然防護','靜謐',
    '撫慰','鼓舞','寬容','熱情','順暢清新','幸福恬靜','歡欣','希望','全新嚮往','清肌調理','溫柔呵護',
    '賦活清新','花漾年華','完美修護','強韌寶貝','復元寶貝','勇氣寶貝','柑橘綻放','樂釋','保衛','仕女',
    '悠活寶貝','舒壓','怡家','新瑞活力','清醇薄荷',
  ];

  // 4 類互斥分類：椰子油優先判斷，接著用產品編號比對，比對不到才用名稱關鍵字備援
  function classifyOil(item){
    const name = (item && item.oil_name) || '';
    const pid = (item && item.product_id) ? String(item.product_id).trim() : '';
    if (name.includes('椰子油')) return 'coconut';
    if (pid && SINGLE_OIL_IDS.has(pid)) return 'single';
    if (pid && BLEND_OIL_IDS.has(pid)) return 'blend';
    if (SINGLE_OIL_KEYWORDS.some(k => name.includes(k) || k.includes(name))) return 'single';
    if (BLEND_OIL_KEYWORDS.some(k => name.includes(k) || k.includes(name))) return 'blend';
    return 'other';
  }

  const statBottles = document.getElementById('stat-bottles');
  const statItems = document.getElementById('stat-items');
  const statSingle = document.getElementById('stat-single');
  const statBlend = document.getElementById('stat-blend');
  const statCoconut = document.getElementById('stat-coconut');
  const statOther = document.getElementById('stat-other');
  const statExpiring = document.getElementById('stat-expiring');
  const searchInput = document.getElementById('inv-search');
  const addBtn = document.getElementById('inv-add-btn');
  const formWrap = document.getElementById('inv-form-wrap');
  const saveBtn = document.getElementById('inv-save-btn');
  const cancelBtn = document.getElementById('inv-cancel-btn');

  const fPid = document.getElementById('inv-f-pid');
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
  let activeCategoryFilter = null; // null | 'single' | 'blend' | 'coconut' | 'other'
  const CATEGORY_LABELS = { single: '單方', blend: '複方', coconut: '椰子油', other: '其他' };

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
    statBottles.textContent = allItems.reduce((sum, i) => sum + (Number(i.quantity) || 0) + (Number(i.in_use) || 0), 0);
    statExpiring.textContent = allItems.filter(i => {
      const d = daysUntil(i.expiry_date);
      return d !== null && d <= 60;
    }).length;
    const counts = { single: 0, blend: 0, coconut: 0, other: 0 };
    allItems.forEach(i => { counts[classifyOil(i)]++; });
    statSingle.textContent = counts.single;
    statBlend.textContent = counts.blend;
    statCoconut.textContent = counts.coconut;
    statOther.textContent = counts.other;
    adminMsg.textContent = '';
    renderList();
  }

  function renderList(){
    const kw = (searchInput.value || '').trim().toLowerCase();
    const filtered = allItems.filter(i => {
      if (kw && !((i.oil_name || '').toLowerCase().includes(kw) || (i.product_id || '').toLowerCase().includes(kw))) return false;
      if (activeCategoryFilter && classifyOil(i) !== activeCategoryFilter) return false;
      return true;
    });

    const activeFilterEl = document.getElementById('inv-active-filter');
    if (activeCategoryFilter) {
      activeFilterEl.style.display = 'flex';
      activeFilterEl.innerHTML = `目前篩選：${CATEGORY_LABELS[activeCategoryFilter]} <button type="button" id="inv-clear-filter">✕ 清除</button>`;
      document.getElementById('inv-clear-filter').addEventListener('click', () => {
        activeCategoryFilter = null;
        document.querySelectorAll('.admin-stat-filter').forEach(el => el.classList.remove('active'));
        renderList();
      });
    } else {
      activeFilterEl.style.display = 'none';
    }

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

      const kInfo = knowledgeMap.get(i.oil_name) || (i.product_id ? knowledgeMap.get(i.product_id) : null);
      let pillarBadge = '';
      let adviceHtml = '';
      if (kInfo) {
        let pClass = 'tag-balance';
        if (kInfo.pillar && kInfo.pillar.includes('右柱')) pClass = 'tag-mercy';
        if (kInfo.pillar && kInfo.pillar.includes('左柱')) pClass = 'tag-severity';
        pillarBadge = `<span class="seal-pill ${pClass}" style="font-size:10px; padding:2px 6px; margin-left:6px;">${kInfo.pillar.split(' ')[0]}</span>`;
        if (kInfo.dilution_guide) {
          let sClass = kInfo.dilution_guide === '直塗' ? 'safety-direct' : kInfo.dilution_guide === '敏感' ? 'safety-sensitive' : 'safety-dilute';
          let sLabel = kInfo.dilution_guide === '直塗' ? '直塗' : kInfo.dilution_guide === '敏感' ? '敏感稀釋' : '必稀釋';
          pillarBadge += `<span class="seal-safety ${sClass}" style="font-size:10px; padding:2px 6px; margin-left:4px;">${sLabel}</span>`;
        }
        if (kInfo.doctor_advice) {
          adviceHtml = `<div style="font-size:11.5px; color:var(--forest-deep); margin-top:5px; line-height:1.6; background:rgba(184,145,46,0.06); padding:4px 8px; border-radius:6px;">🌿 ${kInfo.doctor_advice}</div>`;
        }
      }

      return `
        <div class="booking-card">
          <div class="booking-card-head">
            <div>
              <div class="booking-receipt" style="display:flex; align-items:center; flex-wrap:wrap;">${i.oil_name}${pillarBadge}</div>
              ${i.product_id ? `<div class="booking-created">產品編號：${i.product_id}</div>` : ''}
            </div>
            ${badge}
          </div>
          <div class="booking-row">庫存 ${i.quantity} ${i.unit || '瓶'}｜使用中 ${i.in_use || 0} ${i.unit || '瓶'}${i.capacity ? '｜容量 ' + i.capacity : ''}</div>
          ${i.expiry_date ? `<div class="booking-row">有效期限：${i.expiry_date}</div>` : ''}
          ${adviceHtml}
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
    fPid.value = item ? (item.product_id || '') : '';
    fName.value = item ? item.oil_name : '';
    fQty.value = item ? item.quantity : '';
    fInUse.value = item ? item.in_use : '';
    fUnit.value = item ? (item.unit || '瓶') : '瓶';
    fCapacity.value = item ? (item.capacity || '') : '';
    fExpiry.value = item ? (item.expiry_date || '') : '';
    fNote.value = item ? (item.note || '') : '';
    formWrap.style.display = 'flex';
  }

  // TODO：換成你們真正的 Apple 捷徑名稱（在「捷徑」App 裡該捷徑的名字）
  const APPLE_SHORTCUT_NAME = 'YOUR-SHORTCUT-NAME';

  const scanBtn = document.getElementById('inv-scan-btn');
  scanBtn.addEventListener('click', () => {
    if (APPLE_SHORTCUT_NAME.startsWith('YOUR-')) {
      adminMsg.textContent = '尚未設定 Apple 捷徑名稱，請在 inventory.js 填入 APPLE_SHORTCUT_NAME';
      return;
    }
    // 捷徑掃描後會直接把資料寫回 Google 試算表，這裡只負責開啟捷徑；
    // 掃描完成後回到這頁，按「同步試算表」把最新資料抓進來即可。
    window.location.href = `shortcuts://run-shortcut?name=${encodeURIComponent(APPLE_SHORTCUT_NAME)}`;
    adminMsg.textContent = '已開啟 Apple 捷徑，掃描完成後記得回來按「同步試算表」';
  });

  addBtn.addEventListener('click', () => openForm(null));
  cancelBtn.addEventListener('click', () => { formWrap.style.display = 'none'; });

  const syncBtn = document.getElementById('inv-sync-btn');
  syncBtn.addEventListener('click', async () => {
    const baseUrl = window.OracleSupabase && window.OracleSupabase.SUPABASE_URL;
    if (!baseUrl) { adminMsg.textContent = 'Supabase 尚未設定，無法同步。'; return; }
    syncBtn.disabled = true;
    adminMsg.textContent = '正在從 Google 試算表同步……';
    try {
      const anonKey = window.OracleSupabase && window.OracleSupabase.SUPABASE_ANON_KEY;
      const res = await fetch(`${baseUrl}/functions/v1/sync-inventory`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${anonKey}` },
      });
      if (res.status === 404) {
        adminMsg.textContent = '同步失敗：找不到 sync-inventory（這支 Edge Function 還沒部署，請執行 supabase functions deploy sync-inventory）';
        syncBtn.disabled = false;
        return;
      }
      const data = await res.json().catch(() => null);
      if (!data) {
        adminMsg.textContent = `同步失敗：伺服器回傳非預期格式（HTTP ${res.status}）`;
      } else if (data.ok) {
        adminMsg.textContent = `同步完成：共讀到 ${data.oilTypes} 種精油、新增 ${data.inserted} 筆、更新 ${data.updated} 筆`;
        await loadData();
      } else {
        adminMsg.textContent = '同步失敗：' + (data.error || '未知錯誤');
      }
    } catch (e) {
      adminMsg.textContent = '同步失敗：' + e.message;
    }
    syncBtn.disabled = false;
  });

  saveBtn.addEventListener('click', async () => {
    const payload = {
      product_id: fPid.value.trim() || null,
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

  document.querySelectorAll('.admin-stat-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.filter;
      activeCategoryFilter = (activeCategoryFilter === key) ? null : key;
      document.querySelectorAll('.admin-stat-filter').forEach(el => el.classList.toggle('active', el.dataset.filter === activeCategoryFilter));
      renderList();
    });
  });

  (async () => {
    if (!client) return;
    const { data: { session } } = await client.auth.getSession();
    if (session) {
      const ok = await checkAdminAndEnter();
      if (ok) enterDashboard();
    }
  })();
})();
