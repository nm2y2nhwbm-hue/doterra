(function(){
  "use strict";

  const LIFF_ID = "2010916161-HrIOEAda";
  const LINE_OA_URL = "https://lin.ee/wubPzzI";

  function isLineContext(){
    try {
      if (window.liff && window.liff.isInClient && window.liff.isInClient()) return true;
    } catch (e) {}
    return /\bLine\//i.test(navigator.userAgent || '');
  }

  function setupExperienceGate(){
    const panel = document.getElementById('experience-panel');
    if (!panel) return;

    const params = new URLSearchParams(window.location.search);
    const incomingCode = (params.get('experience_code') || '').trim();

    // 從 LINE / LIFF QR 入口回來時，才顯示這次的專屬體驗碼。
    if (incomingCode && /^INSIGHT-[A-Z0-9]+$/i.test(incomingCode)) {
      panel.dataset.experienceUnlocked = '1';
      panel.style.display = 'block';
      panel.innerHTML = `
        <div class="ep-label">妳的專屬貴賓體驗碼</div>
        <div class="ep-code">${incomingCode}</div>
        <div class="ep-desc">已透過 LINE 入口解鎖。可將此碼提供給 LINE 顧問，或直接帶入貴賓體驗預約。</div>
        <button type="button" class="ep-send-btn" id="ep-open-oa-btn">開啟 LINE 官方帳號</button>
        <a class="ep-book-link" href="booking.html?code=${encodeURIComponent(incomingCode)}">或直接預約貴賓體驗 →</a>`;
      const openOaBtn = panel.querySelector('#ep-open-oa-btn');
      if (openOaBtn) {
        openOaBtn.addEventListener('click', () => {
          window.location.href = LINE_OA_URL;
        });
      }
      const status = document.getElementById('send-status');
      if (status) status.textContent = '體驗碼已在 LINE 入口解鎖 ✓';
      return;
    }

    function gateRenderedCode(){
      if (isLineContext() || panel.dataset.experienceUnlocked === '1' || panel.dataset.experienceGated === '1') return;
      const codeEl = panel.querySelector('.ep-code');
      if (!codeEl) return;
      const code = (codeEl.textContent || '').trim();
      if (!/^INSIGHT-[A-Z0-9]+$/i.test(code)) return;

      const liffUrl = `https://liff.line.me/${LIFF_ID}?experience_code=${encodeURIComponent(code)}`;
      const qrSrc = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(liffUrl)}`;

      panel.dataset.experienceGated = '1';
      panel.innerHTML = `
        <div class="ep-label">LINE 貴賓體驗入口</div>
        <div class="ep-desc">請先用 LINE 掃描下方 QR Code。進入 LINE 後，才會顯示本次專屬體驗碼。</div>
        <div class="gate-qr"><img src="${qrSrc}" alt="LINE 體驗碼入口 QR Code"></div>
        <a class="ep-send-btn" href="${liffUrl}">手機請用 LINE 開啟</a>
        <div class="ep-desc">體驗碼不會在一般瀏覽器直接公開。</div>`;

      const status = document.getElementById('send-status');
      if (status) status.textContent = '';
    }

    gateRenderedCode();
    const observer = new MutationObserver(gateRenderedCode);
    observer.observe(panel, { childList: true, subtree: true });
  }

  const GUIDE_CONTENT = [
    {
      num: '01', title: '單張心靈小語',
      how: '洗牌時在心中默念「當下所需的心靈小語是什麼？」抽出一張，作為今日或此刻的心靈肯定與指引。',
      when: '每天早晨或有需要時，快速聽見當下的內在訊息。',
      diagram: ['指引'],
    },
    {
      num: '02', title: '生活導引牌陣',
      how: '洗牌後抽兩張牌。第一張放左邊，代表目前整體狀況；第二張放右邊，代表生活中所需的建議與方向。',
      when: '想了解現階段狀態、找方向的時候。',
      diagram: ['整體狀況', '建議'],
    },
    {
      num: '03', title: '療癒身心靈牌陣',
      how: '心中默念「目前我的身心靈所需要的是什麼？」抽三張牌：第一張置下方代表身；第二張置左上方代表心；第三張置右上方代表靈。',
      when: '想從身、心、靈三個層面全方位檢視自己時。',
      diagram: ['心', '靈', '身'],
    },
    {
      num: '04', title: '了解自我牌陣',
      how: '思考「別人眼中的自己、私底下的自己、真正的自己，是如何呈現的？」抽三張牌，由左至右依序代表這三個層面。',
      when: '想探索自我認同、內外落差時。',
      diagram: ['別人眼中', '私下獨處', '真正的你'],
    },
    {
      num: '05', title: '單一指示牌陣',
      how: '先選擇一張代表你關注主題的指示牌，置入牌組重新洗牌，再抽出指示牌左右兩側的精油牌，分別代表提升用油與心靈小語。',
      when: '已經有明確的困擾主題，想針對它獲得具體對應占卜時。',
      diagram: ['左側用油', '指示牌', '右側小語'],
    },
    {
      num: '06', title: '主題時間流',
      how: '選定一張想關注的主題卡，置入油卡牌組重新洗牌，抽出主題卡左右兩側的精油牌，分別代表過去成因與未來轉化方向。',
      when: '想針對某個具體主題，看見它的來龍去脈時。',
      diagram: ['過去成因', '主題', '未來轉化'],
    },
    {
      num: '07', title: '生命大運流年・看流年',
      how: '抽三張油卡，依序代表前期殘留的狀態、當下核心課題、後續可以留意的方向。',
      when: '想檢視一整年身心狀態的變化脈絡時。',
      diagram: ['前期', '當下', '後續'],
    },
    {
      num: '08', title: '生命大運流年・看流月',
      how: '抽三張油卡，依序代表這個月的月初、月中、月底三個階段。',
      when: '想檢視這個月身心狀態的變化脈絡時。',
      diagram: ['月初', '月中', '月底'],
    },
    {
      num: '09', title: '生命大運流年・看流日',
      how: '抽三張油卡，依序代表稍早、此刻、稍晚三個時段。',
      when: '想檢視一天之內身心狀態的變化脈絡時。',
      diagram: ['稍早', '此刻', '稍晚'],
    },
    {
      num: '10', title: '年度生命軌跡',
      how: '不使用精油卡，純粹從 12 張主題卡中抽兩張，分別代表上半年與下半年的生命重心。',
      when: '想從較長的時間跨度，看見整體生命焦點的位移時。',
      diagram: ['上半年', '下半年'],
    },
    {
      num: '11', title: '二選一未來抉擇',
      how: '心中分別想著方案 A、方案 B，抽四張油卡：A 的心境、A 的發展、B 的心境、B 的發展。',
      when: '卡在兩個具體方案之間，想對照兩條路的身心感受時。',
      diagram: ['方案A心境', '方案A發展', '方案B心境', '方案B發展'],
    },
    {
      num: '12', title: '三選一十字路口',
      how: '系統會固定顯示「十字路口」主題卡作為核心背景，接著盲抽三張油卡，分別對應三個不同的選擇方向。',
      when: '面臨三個以上的選項、需要多方比較時。',
      diagram: ['核心', '選項一', '選項二', '選項三'],
    },
  ];

  function setupHomeGuide(){
    const link = document.getElementById('home-guide-link');
    if (!link) return;

    let modal = null;
    function ensureModal(){
      if (modal) return modal;
      modal = document.createElement('div');
      modal.className = 'guide-modal';
      modal.innerHTML = `
        <div class="guide-modal-card">
          <button type="button" class="guide-modal-close" aria-label="關閉">✕</button>
          <div class="guide-modal-eyebrow">GUIDE BOOK</div>
          <div class="guide-modal-title">卡牌說明書</div>
          <div class="guide-modal-sub">請先安靜洗牌，將注意力放回此刻，再依問題選擇牌陣。</div>
          <div class="guide-grid">
            ${GUIDE_CONTENT.map(g => `
              <div class="guide-item">
                <div class="gi-num">${g.num}</div>
                <div class="gi-title">${g.title}</div>
                <div class="gi-h">使用方法</div>
                <div class="gi-p">${g.how}</div>
                <div class="gi-h">適用範圍</div>
                <div class="gi-p">${g.when}</div>
                <div class="guide-diagram">
                  ${g.diagram.map(d => `<div class="gd-box${g.diagram.length === 1 ? ' gd-circle' : ''}">${d}</div>`).join('')}
                </div>
              </div>`).join('')}
          </div>
        </div>`;
      document.body.appendChild(modal);
      const close = () => modal.classList.remove('open');
      modal.querySelector('.guide-modal-close').addEventListener('click', close);
      modal.addEventListener('click', (e) => { if (e.target === modal) close(); });
      return modal;
    }

    const open = (e) => {
      if (e) e.preventDefault();
      ensureModal().classList.add('open');
    };
    link.addEventListener('click', open);

    if (new URLSearchParams(window.location.search).get('guide') === '1') open();
  }

  setupExperienceGate();
  setupHomeGuide();
})();
