(() => {
  // ---------- 分類選單（首頁只顯示 3 大分類，12 個子模式列表留在 cards.html） ----------
  const categoryRow = document.getElementById('home-category-row');

  function renderCategoryCards(){
    categoryRow.innerHTML = Object.keys(window.CATEGORY_CATALOG).map(key => {
      const cat = window.CATEGORY_CATALOG[key];
      return `
        <a class="category-card" href="cards.html?cat=${key}" style="text-decoration:none;">
          <div class="cc-icon">${cat.icon}</div>
          <div class="cc-name">${cat.name}</div>
          <div class="cc-tagline">${cat.tagline}</div>
        </a>`;
    }).join('');
  }

  renderCategoryCards();

  // ---------- LOG4 輕量版留資料表單 ----------
  const qlForm = document.getElementById('quick-lead-form');
  const qlName = document.getElementById('ql-name');
  const qlEmail = document.getElementById('ql-email');
  const qlLine = document.getElementById('ql-line');
  const qlConcern = document.getElementById('ql-concern');
  const qlBtn = document.getElementById('ql-submit-btn');
  const qlMsg = document.getElementById('ql-msg');

  qlForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const name = qlName.value.trim();
    const email = qlEmail.value.trim();
    const lineId = qlLine.value.trim();
    const concern = qlConcern.value;

    if (!name || !email) {
      qlMsg.textContent = '請填寫姓名與 E-mail，方便我們與你確認。';
      return;
    }

    qlBtn.disabled = true;
    qlMsg.textContent = '送出中……';

    const fields = {
      name,
      email,
      lineId,
      mainConcern: concern,
    };

    const submit = (window.OracleSupabase && window.OracleSupabase.createBooking)
      ? window.OracleSupabase.createBooking(fields)
      : Promise.resolve({ receiptNo: null, persisted: false, error: 'Supabase 尚未載入' });

    const { receiptNo, persisted, error } = await submit;
    qlBtn.disabled = false;

    if (persisted && receiptNo) {
      qlMsg.textContent = `已收到，受付編號 ${receiptNo}。想現在就抽卡，或想留下更完整的預約資訊，都可以點下方「立即預約」。`;
      qlForm.reset();
    } else {
      qlMsg.textContent = `尚未成功送出${error ? '（' + error + '）' : ''}，請改用下方「立即預約」填寫完整表單。`;
    }
  });
})();
