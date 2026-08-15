(function(){
  "use strict";

  const API_BASE = "https://doterra-73pv.onrender.com";
  const LIFF_ID = "2010916161-HrIOEAda";
  const LINE_OA_URL = "https://lin.ee/wubPzzI";
  const LINE_FOLLOW_KEY = "oc_line_follow_confirmed";

  const modeSelect = document.getElementById('mode-select');
  const categoryRow = document.getElementById('category-row');
  const categoryDetail = document.getElementById('category-detail');
  const cdEyebrow = document.getElementById('cd-eyebrow');
  const cdTitle = document.getElementById('cd-title');
  const cdSub = document.getElementById('cd-sub');
  const cdModes = document.getElementById('cd-modes');
  const stage = document.getElementById('stage');
  const stageTitle = document.getElementById('stage-title');
  const instruction = document.getElementById('instruction');
  const indicatorSelect = document.getElementById('indicator-select');
  const mode5Intro = document.getElementById('mode5-intro');
  const mode5ReadyBtn = document.getElementById('mode5-ready-btn');
  const fanWrap = document.getElementById('fan-wrap');
  const fanStage = document.getElementById('fan-stage');
  const deckHint = document.getElementById('deck-hint');
  const drawnRow = document.getElementById('drawn-row');
  const experiencePanel = document.getElementById('experience-panel');
  const sendStatus = document.getElementById('send-status');
  const againBtn = document.getElementById('again-btn');
  const backBtn = document.getElementById('back-btn');

  let OILS = [];
  let INDICATORS = [];
  let liffReady = false;
  let liffProfile = null;

  // 分類資料改由 mode-catalog.js 提供（首頁與這裡共用同一份，避免文字各改各的）
  const CATEGORY_CONFIG = window.CATEGORY_CATALOG;

  // 注意：title / category / desc 需與 mode-catalog.js 的 MODE_CATALOG 保持一致
  const MODE_CONFIG = {
    1: { title: "今日能量", category: 'mirror', desc: '單張心靈肯定小語', count: 1, labels: ["今日心靈小語"] },
    2: { title: "生活導引", category: 'mirror', desc: '現階段狀態與方向指引', count: 2, labels: ["目前整體狀況", "生活中所需的建議及方向"] },
    3: { title: "三牌陣",   category: 'mirror', desc: '身・心・靈全方位深度解析', count: 3, labels: ["身・目前身體狀況", "心・目前心理狀態", "靈・目前精神狀況"] },
    4: { title: "了解自我", category: 'mirror', desc: '別人眼中的你與真正的你', count: 3, labels: ["別人眼中的你", "私底下獨處時的你", "真正自我的你"] },
    5: { title: "指示牌",   category: 'mirror', desc: '單一指示牌與精油對應占卜' },
    6: {
      title: "主題時間流", category: 'river', desc: '選定主題卡，看過去成因與未來轉化',
      sandwich: {
        center: (name) => `此刻想探索的主題：${name}`,
        left:   (name) => `回望：關於「${name}」，你留意到哪些情緒或慣性？`,
        right:  (name) => `展望：關於「${name}」，你想帶著什麼樣的意圖繼續往前？`,
      },
      prescriptionIndices: [2],
    },
    7: {
      title: "生命大運流年・看流年", category: 'river', desc: '回望前期、當下課題、展望後續', pool: "oils",
      labels: ["回望：這段時間裡，有哪些狀態你還沒放下？", "此刻：目前最需要你留意的課題是什麼？", "展望：接下來，你想為自己準備什麼樣的陪伴？"],
      prescriptionIndices: [2],
    },
    8: {
      title: "生命大運流年・看流月", category: 'river', desc: '月初、月中、月底的狀態變化', pool: "oils",
      labels: ["月初：這個月延續下來的身心狀態是什麼？", "月中：此刻正在浮現的情緒重點是什麼？", "月底：你可以為自己安排什麼樣的能量出口？"],
      prescriptionIndices: [2],
    },
    9: {
      title: "生命大運流年・看流日", category: 'river', desc: '稍早、此刻、稍晚的一日流動', pool: "oils",
      labels: ["稍早：昨日或今早，你留下了什麼樣的感受？", "此刻：今天最需要你面對的狀態是什麼？", "稍晚：晚一點，你想給自己什麼樣的陪伴？"],
      prescriptionIndices: [2],
    },
    10: {
      title: "年度生命軌跡", category: 'river', desc: '純主題卡，看上下半年的重心位移', pool: "indicators",
      labels: ["上半年：這段時間，你的重心可能放在哪裡？", "下半年：接下來，你想把焦點轉向哪裡？"],
    },
    11: {
      title: "二選一未來抉擇", category: 'crossroad', desc: '兩個方案的當下心境與發展對照', pool: "oils",
      labels: ["方案 A：此刻你的心情與考量是什麼？", "方案 A：走這條路，你想為自己留意什麼？", "方案 B：此刻你的心情與考量是什麼？", "方案 B：走這條路，你想為自己留意什麼？"],
      prescriptionIndices: [1, 3],
    },
    12: {
      title: "三選一十字路口", category: 'crossroad', desc: '固定十字路口卡，盲抽三條岔路', pool: "oils",
      fixedIndicatorName: "十字路口",
      labels: ["核心：你正站在一個需要選擇的時刻", "選項一：走這個方向，你想留意什麼樣的感受？", "選項二：走這個方向，你想留意什麼樣的感受？", "選項三：走這個方向，你想留意什麼樣的感受？"],
      prescriptionIndices: [1, 2, 3],
    },
  };

  const INDICATOR_THEMES = {
    "魚": "若你的問題與金錢有關，使內在與外在能夠處於平衡狀態",
    "愛心": "若你的問題與愛情有關",
    "戒指": "若你的問題與婚姻有關",
    "孩童": "若你的問題與孩子有關",
    "狗": "若你的問題與朋友有關",
    "月亮": "若你的問題與名聲或成就有關",
    "樹": "若你的問題與健康有關",
    "十字路口": "若你的問題與下決定有關",
    "船": "若你的問題與旅行有關",
    "鸛鳥": "若你的問題與改變或升遷有關",
    "房屋": "若你的問題與家有關",
    "熊": "若你的問題與老闆有關",
  };

  const FAN_POOL_TARGET = 50; // 想呈現的牌陣密度（目標張數，實際會依精油資料庫數量自動封頂）
  function fanPoolSize(){ return Math.max(3, Math.min(FAN_POOL_TARGET, OILS.length)); }
  let fanItems = [];
  let drawPlan = [];
  let drawnCount = 0;
  let selectedIndicatorName = null;
  let isMode5 = false;
  let currentMode = null;
  let collectedResults = [];

  async function loadData(){
    const [oilsRes, indRes] = await Promise.all([
      fetch(`${API_BASE}/api/oils`),
      fetch(`${API_BASE}/api/indicators`)
    ]);
    OILS = await oilsRes.json();
    INDICATORS = await indRes.json();
  }

  function shuffle(arr){
    const a = arr.slice();
    for(let i=a.length-1;i>0;i--){
      const j = Math.floor(Math.random()*(i+1));
      [a[i],a[j]]=[a[j],a[i]];
    }
    return a;
  }

  function resetStageDom(){
    indicatorSelect.style.display = 'none';
    indicatorSelect.innerHTML = '';
    mode5Intro.style.display = 'none';
    fanWrap.style.display = 'none';
    fanStage.innerHTML = '';
    fanStage.classList.remove('shuffling');
    drawnRow.innerHTML = '';
    experiencePanel.innerHTML = '';
    experiencePanel.style.display = 'none';
    sendStatus.textContent = '';
    againBtn.style.display = 'none';
    const existingO2O = document.getElementById('o2o-panel');
    if (existingO2O) existingO2O.remove();
    fanItems = [];
    drawPlan = [];
    drawnCount = 0;
    selectedIndicatorName = null;
    isMode5 = false;
    collectedResults = [];
  }

  function showModeSelect(){
    stage.classList.remove('active');
    modeSelect.style.display = 'flex';
  }

  let selectedCategory = 'mirror';

  function renderCategoryDetail(catKey){
    selectedCategory = catKey;
    const cat = CATEGORY_CONFIG[catKey];
    categoryRow.querySelectorAll('.category-card').forEach(el => {
      el.classList.toggle('active', el.dataset.cat === catKey);
    });
    cdEyebrow.textContent = cat.eyebrow;
    cdTitle.textContent = `${cat.name} → ${cat.tagline}`;
    cdSub.textContent = cat.sub;
    cdModes.innerHTML = cat.modes.map(m => {
      const cfg = MODE_CONFIG[m];
      const num = String(m).padStart(2, '0');
      return `<div class="mode-btn" data-mode="${m}"><div class="mode-num">${num}</div><div class="mode-text"><b>${cfg.title}</b><span>${cfg.desc || ''}</span></div></div>`;
    }).join('');
  }

  categoryRow.addEventListener('click', (e) => {
    const card = e.target.closest('.category-card');
    if (!card) return;
    renderCategoryDetail(card.dataset.cat);
  });

  renderCategoryDetail(selectedCategory);

  function enterStage(modeId){
    modeSelect.style.display = 'none';
    stage.classList.add('active');
    resetStageDom();
    currentMode = modeId;

    if (modeId === 5 || modeId === 6) {
      isMode5 = true;
      stageTitle.textContent = MODE_CONFIG[modeId] ? MODE_CONFIG[modeId].title : '指示牌';
      renderMode5Intro();
      return;
    }

    if (modeId === 12) {
      startFixedIndicatorMode();
      return;
    }

    const cfg = MODE_CONFIG[modeId];
    stageTitle.textContent = cfg.title;
    drawPlan = cfg.labels;
    const poolSource = cfg.pool === 'indicators' ? INDICATORS : OILS;
    const poolSize = cfg.pool === 'indicators' ? Math.min(12, poolSource.length) : fanPoolSize();
    const pool = shuffle(poolSource).slice(0, poolSize).map(c => ({card:c, isIndicator:false}));
    startShuffleThenFan(pool);
  }

  function startFixedIndicatorMode(){
    const cfg = MODE_CONFIG[currentMode];
    stageTitle.textContent = cfg.title;
    const fixedCard = INDICATORS.find(i => i.name === cfg.fixedIndicatorName);
    drawPlan = cfg.labels.slice(1);
    const pool = shuffle(OILS).slice(0, fanPoolSize()).map(c => ({card:c, isIndicator:false}));
    startShuffleThenFan(pool);
    if (fixedCard) {
      renderDrawnCard(cfg.labels[0], fixedCard);
      collectedResults.push({ label: cfg.labels[0], card: fixedCard });
    } else {
      instruction.textContent = `找不到「${cfg.fixedIndicatorName}」指示卡資料，請確認指示卡資料庫。`;
    }
  }

  function renderMode5Intro(){
    instruction.textContent = '';
    mode5Intro.style.display = 'flex';
  }

  mode5ReadyBtn.addEventListener('click', () => {
    mode5Intro.style.display = 'none';
    instruction.textContent = '請先從下方選擇一個你想探索的主題';
    renderIndicatorList();
  });

  function renderIndicatorList(){
    indicatorSelect.style.display = 'flex';
    INDICATORS.forEach(ind => {
      const item = document.createElement('div');
      item.className = 'indicator-item';
      const theme = INDICATOR_THEMES[ind.name] || '';
      item.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:2px;">
          <span><b>${ind.name}</b> <span class="en">${ind.name_en || ''}</span></span>
          <span style="font-size:11.5px;color:#8a7c6c;">${theme}</span>
        </div>`;
      item.addEventListener('click', () => {
        selectedIndicatorName = ind.name;
        indicatorSelect.style.display = 'none';
        proceedWithIndicator(ind);
      });
      indicatorSelect.appendChild(item);
    });
  }

  function proceedWithIndicator(ind){
    instruction.textContent = `「${ind.name}」已插入牌組，正在洗牌……洗牌之後，抽三張牌～`;

    const oilsSubset = shuffle(OILS).slice(0, fanPoolSize() - 1).map(c => ({card:c, isIndicator:false}));
    const insertPos = Math.floor(Math.random() * (oilsSubset.length + 1));
    oilsSubset.splice(insertPos, 0, {card: ind, isIndicator:true});
    const finalDeck = shuffle(oilsSubset);

    startShuffleThenFan(finalDeck, true);
  }

  // ---------- 馬蹄形 U 型佈局：單一連續參數曲線 ----------
  // 整條路徑（左臂頂端 → 左臂/圓弧交界 → 圓弧底部 → 圓弧/右臂交界 → 右臂頂端）
  // 由同一個函式 rawHorseshoePoint(p) 依 p∈[0,1] 連續計算座標與切線角度，
  // 兩側直臂與底部圓弧在交界處位置、切線方向皆連續銜接（非三段硬接）。
  // 位置再依「弧長」重新取樣，讓從頂端到底部的牌卡密度全程一致。

  function computeHorseshoeParams(containerW, containerH, cardH){
    const topPad = cardH * 1.02;               // 近直立的中央牌會整張凸出頂端，預留空間
    const bottomPad = Math.max(10, cardH * 0.12);
    const availableH = Math.max(containerH - topPad - bottomPad, cardH * 2);

    let R = (containerW * 0.74) / 2;            // U 形最大寬度 ≈ 容器寬度的 74%
    let armLength = availableH - R;
    if (armLength < R) {
      // 容器偏矮或偏寬時，縮小寬度而非放大，確保「高度明顯大於寬度」且不超出容器
      R = availableH / 2.3;
      armLength = availableH - R;
    }
    armLength = Math.max(armLength, R * 0.3);

    return { R, armLength, bottomPad };
  }

  function rawHorseshoePoint(p, params){
    const { R, armLength } = params;
    const arcLen = Math.PI * R;
    const total = armLength * 2 + arcLen;
    const p1 = armLength / total;
    const p2 = (armLength + arcLen) / total;

    let x, y;
    if (p <= p1) {                              // 左臂：頂端 → 交界，垂直直線 x=-R 全程不變
      const s = p1 === 0 ? 0 : p / p1;
      const u = 1 - s;
      x = -R;
      y = -armLength * u;
    } else if (p <= p2) {                        // 底部圓弧：左交界 → 右交界，完整半圓
      const s2 = (p2 === p1) ? 0 : (p - p1) / (p2 - p1);
      const theta = (180 + s2 * 180) * Math.PI / 180;
      x = R * Math.cos(theta);
      y = -R * Math.sin(theta);
    } else {                                      // 右臂：交界 → 頂端，垂直直線 x=+R 全程不變
      const s3 = (1 - p2) === 0 ? 0 : (p - p2) / (1 - p2);
      const u = s3;
      x = R;
      y = -armLength * u;
    }

    // 單一連續函式決定切線旋轉角：左臂頂端≈+90°(近乎平躺)、底部中央=0°(直立)、右臂頂端≈-90°
    const angle = 90 * Math.cos(Math.PI * p);
    return { x, y, angle };
  }

  function sampleHorseshoe(params, resolution){
    const pts = [];
    for (let i = 0; i <= resolution; i++){
      const p = i / resolution;
      const pt = rawHorseshoePoint(p, params);
      pts.push({ p, x: pt.x, y: pt.y, angle: pt.angle, len: 0 });
    }
    let acc = 0;
    for (let i = 1; i < pts.length; i++){
      const dx = pts[i].x - pts[i-1].x, dy = pts[i].y - pts[i-1].y;
      acc += Math.sqrt(dx*dx + dy*dy);
      pts[i].len = acc;
    }
    return { pts, totalLen: acc };
  }

  function pointAtLength(sample, targetLen){
    const { pts, totalLen } = sample;
    if (targetLen <= 0) return pts[0];
    if (targetLen >= totalLen) return pts[pts.length - 1];
    let lo = 0, hi = pts.length - 1;
    while (lo < hi - 1){
      const mid = (lo + hi) >> 1;
      if (pts[mid].len < targetLen) lo = mid; else hi = mid;
    }
    const a = pts[lo], b = pts[hi];
    const t = (b.len - a.len) === 0 ? 0 : (targetLen - a.len) / (b.len - a.len);
    return {
      x: a.x + (b.x - a.x) * t,
      y: a.y + (b.y - a.y) * t,
      angle: a.angle + (b.angle - a.angle) * t,
    };
  }

  function layoutFan(){
    const n = fanItems.length;
    if (!n) return;

    const rect = fanStage.getBoundingClientRect();
    const containerW = rect.width || fanStage.clientWidth || 320;
    const containerH = rect.height || fanStage.clientHeight || 440;

    const sampleEl = fanItems[0].el;
    const cardW = (sampleEl && sampleEl.offsetWidth) || 68;
    const cardH = (sampleEl && sampleEl.offsetHeight) || 95;

    const params = computeHorseshoeParams(containerW, containerH, cardH);
    const sample = sampleHorseshoe(params, 480);

    // 牌數過多、等距間隔小於可辨識的最小露出邊寬時，縮小牌面而非撐寬 U 形
    const spacing = n > 1 ? sample.totalLen / (n - 1) : sample.totalLen;
    const minVisibleEdge = Math.max(10, cardW * 0.22);
    const cardScale = (n > 1 && spacing < minVisibleEdge)
      ? Math.max(0.42, spacing / minVisibleEdge)
      : 1;

    const curveCenterX = containerW / 2;
    const curveBottomY = containerH - params.bottomPad;
    const offsetY = curveBottomY - params.R;

    fanItems.forEach((item, i) => {
      const targetLen = n > 1 ? (i / (n - 1)) * sample.totalLen : sample.totalLen / 2;
      const pt = pointAtLength(sample, targetLen);
      const px = curveCenterX + pt.x;
      const py = offsetY + pt.y;

      const w = cardW * cardScale, h = cardH * cardScale;
      item.el.style.width = w + 'px';
      item.el.style.height = h + 'px';
      item.el.style.left = (px - w / 2) + 'px';
      item.el.style.top = (py - h) + 'px';
      item.el.style.transform = `rotate(${pt.angle}deg)`;
      item.el.style.zIndex = i;
    });
  }

  let fanResizeRAF = null;
  window.addEventListener('resize', () => {
    if (fanWrap.style.display !== 'flex' || !fanItems.length) return;
    if (fanResizeRAF) cancelAnimationFrame(fanResizeRAF);
    fanResizeRAF = requestAnimationFrame(layoutFan);
  });

  function startShuffleThenFan(deckItems, mode5){
    fanWrap.style.display = 'flex';
    fanStage.style.display = '';
    fanStage.innerHTML = '';
    fanStage.classList.add('shuffling');
    deckHint.textContent = '正在洗牌，請稍候……';
    drawnRow.innerHTML = '';
    experiencePanel.innerHTML = '';
    experiencePanel.style.display = 'none';
    const existingO2O2 = document.getElementById('o2o-panel');
    if (existingO2O2) existingO2O2.remove();
    drawnCount = 0;
    collectedResults = [];

    fanItems = deckItems.map(d => ({ ...d, el: null }));

    setTimeout(() => {
      fanStage.classList.remove('shuffling');
      fanItems.forEach((item) => {
        const el = document.createElement('div');
        el.className = 'fan-card';
        fanStage.appendChild(el);
        item.el = el;
      });
      layoutFan();

      if (mode5) {
        deckHint.textContent = '點擊扇形中任一張牌，感應你的指示牌位置';
        fanItems.forEach(item => {
          item.el.addEventListener('click', () => revealMode5());
        });
      } else {
        deckHint.textContent = `依序點擊卡牌，抽出第 1 張（共需 ${drawPlan.length} 張）`;
        fanItems.forEach(item => {
          item.el.addEventListener('click', () => drawStandardCard(item));
        });
      }
    }, 900);
  }

  function flipCardInPlace(item, label){
    item.el.classList.add('revealed');
    item.el.innerHTML = `<img src="${item.card.image_url}" alt="${item.card.name}"><div class="mini-cap">${item.card.name}</div>`;
  }

  function drawStandardCard(item){
    if (item.el.classList.contains('revealed') || item.el.classList.contains('dimmed')) return;
    if (drawnCount >= drawPlan.length) return;

    const label = drawPlan[drawnCount];
    flipCardInPlace(item, label);
    renderDrawnCard(label, item.card);
    collectedResults.push({ label, card: item.card });
    drawnCount++;

    if (drawnCount >= drawPlan.length) {
      deckHint.textContent = '解讀完成 ✦ 願這份訊息與你同在';
      fanItems.forEach(i => { if(!i.el.classList.contains('revealed')) i.el.classList.add('dimmed'); });
      finishAndSend();
    } else {
      deckHint.textContent = `依序點擊卡牌，抽出第 ${drawnCount + 1} 張（共需 ${drawPlan.length} 張）`;
    }
  }

  function revealMode5(){
    if (drawnCount > 0) return;
    drawnCount = 1;

    const idx = fanItems.findIndex(i => i.isIndicator);
    const leftIdx = idx - 1;
    const rightIdx = idx + 1;

    fanItems.forEach((item, i) => {
      if (i === idx || i === leftIdx || i === rightIdx) {
        item.el.classList.add('spotlight');
      } else {
        item.el.classList.add('dimmed');
      }
    });

    const sandwichCfg = MODE_CONFIG[currentMode] && MODE_CONFIG[currentMode].sandwich;
    const centerLabel = sandwichCfg ? sandwichCfg.center(selectedIndicatorName) : '指示牌';
    const leftLabel = sandwichCfg ? sandwichCfg.left(selectedIndicatorName) : `「${selectedIndicatorName}」左側提升精油`;
    const rightLabel = sandwichCfg ? sandwichCfg.right(selectedIndicatorName) : `「${selectedIndicatorName}」右側提升精油`;

    deckHint.textContent = `「${selectedIndicatorName}」指示牌現身，為你點出主題……`;

    const indicatorItem = fanItems[idx];
    flipCardInPlace(indicatorItem, centerLabel);
    renderDrawnCard(centerLabel, indicatorItem.card);
    collectedResults.push({ label: centerLabel, card: indicatorItem.card });

    setTimeout(() => {
      deckHint.textContent = '正在揭示左右兩側的精油指引……';

      const revealSide = (sideIdx, label, delay) => {
        setTimeout(() => {
          if (sideIdx < 0 || sideIdx >= fanItems.length) return;
          const sideItem = fanItems[sideIdx];
          flipCardInPlace(sideItem, label);
          renderDrawnCard(label, sideItem.card);
          collectedResults.push({ label, card: sideItem.card });
        }, delay);
      };
      revealSide(leftIdx, leftLabel, 0);
      revealSide(rightIdx, rightLabel, 500);

      setTimeout(() => {
        deckHint.textContent = '解讀完成 ✦ 願這份訊息與你同在';
        finishAndSend();
      }, 1100);
    }, 900);
  }

  function renderDrawnCard(label, card){
    const slot = document.createElement('div');
    slot.className = 'drawn-slot';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'drawn-card';
    btn.innerHTML = `
      <div class="slot-label">${label}</div>
      <img src="${card.image_url}" alt="${card.name}">
      <div class="cap"><b>${card.name}</b><span>${card.name_en || ''}</span></div>
      <div class="read-link">閱讀訊息 →</div>`;
    btn.addEventListener('click', () => openInsightModal(label, card));
    slot.appendChild(btn);
    drawnRow.appendChild(slot);
  }

  function splitKeywords(keywords){
    if (!keywords) return [];
    return keywords.split(/[,，、\s]+/).map(s => s.trim()).filter(Boolean);
  }

  let insightModalEl = null;
  function ensureInsightModal(){
    if (insightModalEl) return insightModalEl;
    const el = document.createElement('div');
    el.className = 'insight-modal';
    el.innerHTML = `
      <div class="insight-modal-card">
        <button type="button" class="insight-modal-close" aria-label="關閉">✕</button>
        <div class="insight-modal-img"><img id="im-img" src="" alt=""></div>
        <div class="insight-modal-body">
          <div class="im-eyebrow" id="im-label"></div>
          <div class="im-name" id="im-name"></div>
          <div class="im-name-en" id="im-name-en"></div>
          <div class="im-pills" id="im-pills"></div>
          <div id="im-locked-content">
            <div class="im-gate">
              <div class="gate-eyebrow">SAVE YOUR INSIGHT</div>
              <div class="gate-title">保存這次的洞悉</div>
              <div class="gate-desc">加入 LINE 官方帳號，即可查看完整訊息，並接收本次抽卡紀錄與後續說明。</div>
              <div class="gate-note">是否加入由您自由選擇；不加入仍可查看本次簡要訊息。</div>
              <div class="gate-qr"><img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(LINE_OA_URL)}" alt="LINE 官方帳號 QR Code"></div>
              <button type="button" class="gate-confirm-btn" id="im-gate-confirm">我已完成加入，查看完整訊息</button>
              <button type="button" class="gate-skip-btn" id="im-gate-skip">暫時略過，查看簡要訊息</button>
            </div>
          </div>
          <div id="im-unlocked-content" style="display:none;">
            <div class="im-guidance" id="im-guidance"></div>
            <div class="im-chakra" id="im-chakra"></div>
          </div>
        </div>
      </div>`;
    document.body.appendChild(el);
    el.querySelector('.insight-modal-close').addEventListener('click', closeInsightModal);
    el.addEventListener('click', (e) => { if (e.target === el) closeInsightModal(); });
    el.querySelector('#im-gate-confirm').addEventListener('click', () => {
      try { localStorage.setItem(LINE_FOLLOW_KEY, '1'); } catch(e){}
      showUnlockedContent(el);
    });
    el.querySelector('#im-gate-skip').addEventListener('click', closeInsightModal);
    insightModalEl = el;
    return el;
  }

  function showUnlockedContent(el){
    el.querySelector('#im-locked-content').style.display = 'none';
    el.querySelector('#im-unlocked-content').style.display = 'block';
  }

  function isLineFollowConfirmed(){
    try { return localStorage.getItem(LINE_FOLLOW_KEY) === '1'; } catch(e){ return false; }
  }

  function openInsightModal(label, card){
    const el = ensureInsightModal();
    el.querySelector('#im-img').src = card.image_url;
    el.querySelector('#im-img').alt = card.name;
    el.querySelector('#im-label').textContent = label;
    el.querySelector('#im-name').textContent = card.name;
    el.querySelector('#im-name-en').textContent = card.name_en || '';
    el.querySelector('#im-pills').innerHTML = splitKeywords(card.keywords)
      .map(k => `<span class="im-pill">${k}</span>`).join('');
    el.querySelector('#im-guidance').textContent = card.guidance || '';
    el.querySelector('#im-chakra').textContent = card.chakra ? `脈輪：${card.chakra}` : '';

    el.querySelector('#im-locked-content').style.display = 'block';
    el.querySelector('#im-unlocked-content').style.display = 'none';
    if (isLineFollowConfirmed()) showUnlockedContent(el);

    el.classList.add('open');
  }

  function closeInsightModal(){
    if (insightModalEl) insightModalEl.classList.remove('open');
  }

  function buildBubble(label, card){
    const bodyContents = [
      {
        type: "box", layout: "baseline",
        contents: [
          { type: "text", text: "關鍵詞", size: "xs", color: "#B08968", flex: 1 },
          { type: "text", text: card.keywords || "無", size: "sm", color: "#555555", flex: 4, wrap: true },
        ],
      },
    ];
    if (card.chakra) {
      bodyContents.unshift({
        type: "box", layout: "baseline",
        contents: [
          { type: "text", text: "脈輪", size: "xs", color: "#B08968", flex: 1 },
          { type: "text", text: card.chakra, size: "sm", color: "#555555", flex: 4, wrap: true },
        ],
      });
    }
    bodyContents.push({ type: "separator", margin: "md" });
    bodyContents.push({ type: "text", text: card.guidance || "無", wrap: true, margin: "md", size: "sm", color: "#333333" });
    if (card.description) {
      bodyContents.push({ type: "separator", margin: "md" });
      bodyContents.push({ type: "text", text: card.description, wrap: true, margin: "md", size: "xs", color: "#777777" });
    }

    return {
      type: "bubble",
      header: {
        type: "box", layout: "vertical",
        contents: [
          { type: "text", text: label, size: "xs", color: "#B08968", align: "center" },
          { type: "text", text: card.name, weight: "bold", size: "xl", align: "center" },
          { type: "text", text: card.name_en || "", size: "sm", align: "center", color: "#888888" },
        ],
      },
      hero: { type: "image", url: card.image_url, size: "full", aspectRatio: "4:3", aspectMode: "cover" },
      body: { type: "box", layout: "vertical", spacing: "sm", contents: bodyContents },
    };
  }

  function logDrawToBackend(){
    if (!collectedResults.length) return;
    const payload = {
      user_id: liffProfile ? liffProfile.userId : '',
      display_name: liffProfile ? liffProfile.displayName : '',
      mode: `mode_${currentMode}`,
      cards: collectedResults.map(r => r.card.name),
    };
    fetch(`${API_BASE}/api/log-draw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }).catch((e) => console.error('[log-draw error]', e));
  }

  function finishAndSend(){
    showAgainButton();
    logDrawToBackend();
    fanStage.style.display = 'none'; // 抽完收起扇形，只留結果卡片，避免跟下面的內容擠在一起

    const modeTitle = MODE_CONFIG[currentMode] ? MODE_CONFIG[currentMode].title : '指示牌';
    renderO2OPrescription();
    const resultsPayload = collectedResults.map(r => ({
      label: r.label, card_name: r.card.name, card_name_en: r.card.name_en || '', image_url: r.card.image_url,
    }));
    const lineUserId = liffProfile ? liffProfile.userId : null;
    const lineDisplayName = liffProfile ? liffProfile.displayName : null;

    const getCode = (window.OracleSupabase && window.OracleSupabase.saveDrawAndGetCode)
      ? window.OracleSupabase.saveDrawAndGetCode(currentMode, resultsPayload, lineUserId, lineDisplayName)
      : Promise.resolve({ code: null, persisted: false });

    getCode.then(({ code, persisted }) => {
      renderExperiencePanel(code, persisted, modeTitle);
    });
  }

  // 模式 6-9：在解牌結果最後，依「未來/解方」位置抽到的精油卡，附上一份通用的
  // 擴香與滾珠調油建議（標準芳療稀釋比例，非醫療劑量指示）。
  function buildO2OSuggestion(card){
    return `擴香建議：3～5 滴「${card.name}」加入擴香機，讓香氣陪伴這段轉化。\n`
      + `滾珠調油：「${card.name}」3～4 滴＋10ml 基底油（如荷荷芭油），約 2% 稀釋濃度，可隨身滾塗於手腕或頸後。`;
  }

  function renderO2OPrescription(){
    const cfg = MODE_CONFIG[currentMode];
    if (!cfg || !cfg.prescriptionIndices || !cfg.prescriptionIndices.length) return;

    const targets = cfg.prescriptionIndices
      .map(i => collectedResults[i])
      .filter(Boolean);
    if (!targets.length) return;

    const existing = document.getElementById('o2o-panel');
    if (existing) existing.remove();

    const el = document.createElement('div');
    el.id = 'o2o-panel';
    el.className = 'o2o-panel';
    el.innerHTML = `
      <div class="o2o-title">🌿 實體精油處方箋</div>
      ${targets.map(t => `
        <div class="o2o-item">
          <div class="o2o-label">${t.label}</div>
          <div class="o2o-card-name">${t.card.name}</div>
          <div class="o2o-text">${buildO2OSuggestion(t.card)}</div>
        </div>`).join('')}
      <div class="o2o-note">以上為一般芳療稀釋比例參考，並非醫療劑量指示；孕期、嬰幼兒或特殊體質請先諮詢專業人員。</div>`;
    drawnRow.insertAdjacentElement('afterend', el);
  }

  function renderExperiencePanel(code, persisted, modeTitle){
    experiencePanel.style.display = 'block';
    experiencePanel.innerHTML = `
      <div class="ep-label">妳的專屬貴賓體驗碼</div>
      <div class="ep-code">${code || '（產生中，請稍候）'}</div>
      <div class="ep-desc">將此碼傳給 LINE 顧問，可詢問本次牌卡與禮盒體驗。${persisted ? '' : '<br>（尚未連接雲端保存，此碼僅供本次顯示）'}</div>
      <button type="button" class="ep-send-btn" id="ep-send-btn">傳送體驗碼，了解禮盒</button>
      <a class="ep-book-link" href="booking.html${code ? '?code=' + encodeURIComponent(code) : ''}">或直接預約貴賓體驗 →</a>`;
    const btn = experiencePanel.querySelector('#ep-send-btn');
    btn.addEventListener('click', () => sendExperienceCode(code, modeTitle));
  }

  function sendExperienceCode(code, modeTitle){
    const btn = experiencePanel.querySelector('#ep-send-btn');
    if (btn) btn.disabled = true;

    if (liffReady && window.liff && liff.isInClient()) {
      const bubbles = collectedResults.map(r => buildBubble(r.label, r.card));
      const altText = `${modeTitle}牌陣結果：` + collectedResults.map(r => r.card.name).join('、');
      const flexMessage = {
        type: "flex",
        altText: altText,
        contents: bubbles.length > 1 ? { type: "carousel", contents: bubbles } : bubbles[0],
      };
      const codeMessage = { type: "text", text: `體驗碼：${code}\n請提供給您的精油顧問，即可了解禮盒體驗 🌿` };

      sendStatus.textContent = '正在將結果送回聊天室……';
      liff.sendMessages([flexMessage, codeMessage]).then(() => {
        sendStatus.textContent = '已送回 LINE 聊天室 ✓';
        if (btn) btn.disabled = false;
      }).catch((err) => {
        const reason = (err && err.message) ? err.message : String(err);
        sendStatus.textContent = `送回聊天室失敗：${reason}`;
        console.error('[liff.sendMessages error]', err);
        if (btn) btn.disabled = false;
      });
    } else {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(code).catch(() => {});
      }
      sendStatus.textContent = '體驗碼已複製，加入 LINE 官方帳號後貼給顧問即可';
      if (LINE_OA_URL && !LINE_OA_URL.includes('YOUR-OA-LINK')) {
        window.open(LINE_OA_URL, '_blank');
      }
      if (btn) btn.disabled = false;
    }
  }

  function showAgainButton(){
    againBtn.style.display = 'inline-block';
  }

  modeSelect.addEventListener('click', (e) => {
    const btn = e.target.closest('.mode-btn');
    if (!btn) return;
    enterStage(Number(btn.dataset.mode));
  });

  backBtn.addEventListener('click', showModeSelect);
  againBtn.addEventListener('click', showModeSelect);

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

  let guideModalEl = null;
  function ensureGuideModal(){
    if (guideModalEl) return guideModalEl;
    const el = document.createElement('div');
    el.className = 'guide-modal';
    el.innerHTML = `
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
    document.body.appendChild(el);
    el.querySelector('.guide-modal-close').addEventListener('click', closeGuideModal);
    el.addEventListener('click', (e) => { if (e.target === el) closeGuideModal(); });
    guideModalEl = el;
    return el;
  }

  function openGuideModal(){ ensureGuideModal().classList.add('open'); }
  function closeGuideModal(){ if (guideModalEl) guideModalEl.classList.remove('open'); }

  const guideBookLink = document.getElementById('guide-book-link');
  if (guideBookLink) {
    guideBookLink.addEventListener('click', (e) => { e.preventDefault(); openGuideModal(); });
  }

  function initFromQuery(){
    const params = new URLSearchParams(window.location.search);
    const m = Number(params.get('mode'));
    if (m >= 1 && m <= 12) enterStage(m);
    if (params.get('guide') === '1') openGuideModal();
    const cat = params.get('cat');
    if (!m && cat && CATEGORY_CONFIG[cat]) renderCategoryDetail(cat);
  }

  function initLiff(){
    if (!window.liff) return Promise.resolve();
    return liff.init({ liffId: LIFF_ID })
      .then(() => {
        liffReady = true;
        if (liff.isLoggedIn && liff.isLoggedIn()) {
          return liff.getProfile().then(p => { liffProfile = p; }).catch(() => {});
        }
      })
      .catch((e) => console.error('[liff.init error]', e));
  }

  Promise.all([loadData(), initLiff()]).then(() => {
    instruction.textContent = '';
    initFromQuery();
    // LINE 使用者沒有「回首頁」的意義（首頁對 LINE 入口會直接轉回這裡），故隱藏該連結
    if (liffReady && window.liff && liff.isInClient && liff.isInClient()) {
      const backHomeLink = document.querySelector('.back-home-link');
      if (backHomeLink) backHomeLink.style.display = 'none';
    }
  }).catch((e) => {
    console.error('[loadData error]', e);
    instruction.textContent = '資料讀取失敗，請重新整理頁面再試一次。';
  });
})();
