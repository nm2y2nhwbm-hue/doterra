(function(){
  "use strict";

  // ⚠️ 請依照 cards.html 實際部署位置調整這裡：
  // 若 cards.html 跑在 Render 上（跟 API 同網域），可以把 API_BASE 改成空字串 ''，
  // 直接用相對路徑 fetch('/api/oils') 即可，不需要跨網域。
  // 若 cards.html 跑在 Vercel（跟 API 不同網域），才需要填完整 Render 網址。
  const API_BASE = "https://doterra-73pv.onrender.com";
  const LIFF_ID = "2010916161-HrIOEAda"; // 雫之洞悉・返魂堂（開發環境）

  const modeSelect = document.getElementById('mode-select');
  const stage = document.getElementById('stage');
  const stageTitle = document.getElementById('stage-title');
  const instruction = document.getElementById('instruction');
  const indicatorSelect = document.getElementById('indicator-select');
  const fanWrap = document.getElementById('fan-wrap');
  const fanStage = document.getElementById('fan-stage');
  const deckHint = document.getElementById('deck-hint');
  const drawnRow = document.getElementById('drawn-row');
  const revealDetail = document.getElementById('reveal-detail');
  const sendStatus = document.getElementById('send-status');
  const againBtn = document.getElementById('again-btn');
  const backBtn = document.getElementById('back-btn');

  let OILS = [];
  let INDICATORS = [];
  let liffReady = false;
  let liffProfile = null;

  const MODE_CONFIG = {
    1: {
      title: "今日能量",
      count: 1,
      labels: ["今日心靈小語"]
    },
    2: {
      title: "生活導引",
      count: 2,
      labels: ["目前整體狀況", "生活中所需的建議及方向"]
    },
    3: {
      title: "三牌陣",
      count: 3,
      labels: [
        "身・目前身體狀況",
        "心・目前心理狀態",
        "靈・目前精神狀況"
      ]
    },
    4: {
      title: "了解自我",
      count: 3,
      labels: [
        "別人眼中的你",
        "私底下獨處時的你",
        "真正自我的你"
      ]
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

  const FAN_POOL_SIZE = 16;

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

    for(let i = a.length - 1; i > 0; i--){
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }

    return a;
  }

  function resetStageDom(){
    indicatorSelect.style.display = 'none';
    indicatorSelect.innerHTML = '';

    fanWrap.style.display = 'none';
    fanStage.innerHTML = '';
    fanStage.classList.remove('shuffling');

    drawnRow.innerHTML = '';

    revealDetail.innerHTML = '';
    revealDetail.classList.remove('active');

    sendStatus.textContent = '';
    againBtn.style.display = 'none';

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

  function enterStage(modeId){
    modeSelect.style.display = 'none';
    stage.classList.add('active');

    resetStageDom();

    currentMode = modeId;

    if(modeId === 5){
      isMode5 = true;
      stageTitle.textContent = '指示牌';
      instruction.textContent = '請先從下方選擇一個你想探索的主題';

      renderIndicatorList();
      return;
    }

    const cfg = MODE_CONFIG[modeId];

    stageTitle.textContent = cfg.title;
    drawPlan = cfg.labels;

    const pool = shuffle(OILS)
      .slice(0, FAN_POOL_SIZE)
      .map(c => ({
        card: c,
        isIndicator: false
      }));

    startShuffleThenFan(pool);
  }

  function renderIndicatorList(){
    indicatorSelect.style.display = 'flex';

    INDICATORS.forEach(ind => {
      const item = document.createElement('div');

      item.className = 'indicator-item';

      const theme = INDICATOR_THEMES[ind.name] || '';

      item.innerHTML = `
        <div style="display:flex;flex-direction:column;gap:2px;">
          <span>
            <b>${ind.name}</b>
            <span class="en">${ind.name_en || ''}</span>
          </span>
          <span style="font-size:11.5px;color:#8a7c6c;">
            ${theme}
          </span>
        </div>
      `;

      item.addEventListener('click', () => {
        selectedIndicatorName = ind.name;
        indicatorSelect.style.display = 'none';

        instruction.textContent =
          `「${ind.name}」已插入牌組，正在洗牌……洗牌之後，抽三張牌～`;

        const oilsSubset = shuffle(OILS)
          .slice(0, FAN_POOL_SIZE - 1)
          .map(c => ({
            card: c,
            isIndicator: false
          }));

        const insertPos =
          Math.floor(Math.random() * (oilsSubset.length + 1));

        oilsSubset.splice(insertPos, 0, {
          card: ind,
          isIndicator: true
        });

        const finalDeck = shuffle(oilsSubset);

        startShuffleThenFan(finalDeck, true);
      });

      indicatorSelect.appendChild(item);
    });
  }

  // ==================================================
  // 唯一更改：
  // 左右直線＋底部半圓的馬蹄形 U
  // ==================================================
  function layoutFan(){
    const n = fanItems.length;

    if(!n) return;

    // 依 LIFF 實際寬度縮放。
    const stageWidth = fanStage.clientWidth || 600;

    // U 型半圓半徑。
    const radius = Math.min(
      240,
      Math.max(125, stageWidth * 0.4)
    );

    // 左右直線段高度。
    const armHeight = Math.min(
      230,
      Math.max(145, stageWidth * 0.38)
    );

    // 底部半圓的路徑長度。
    const arcLength = Math.PI * radius;

    // 左直線＋底部半圓＋右直線。
    const totalLength =
      armHeight * 2 + arcLength;

    // 確保舞台有足夠空間容納完整馬蹄形。
    fanStage.style.height =
      `${Math.ceil(armHeight + radius + 125)}px`;

    fanItems.forEach((item, i) => {
      const t =
        n === 1 ? 0.5 : i / (n - 1);

      const distance =
        t * totalLength;

      let x;
      let y;
      let rotation;

      if(distance < armHeight){
        // 左側直線：由上往下。
        x = -radius;
        y = distance;
        rotation = 0;

      }else if(distance <= armHeight + arcLength){
        // 底部半圓：
        // 由左側繞過底部，再走到右側。
        const arcDistance =
          distance - armHeight;

        const angle =
          Math.PI + arcDistance / radius;

        x = Math.cos(angle) * radius;

        y =
          armHeight -
          Math.sin(angle) * radius;

        rotation =
          (angle - Math.PI) *
          180 /
          Math.PI;

      }else{
        // 右側直線：由下往上。
        const rightDistance =
          distance -
          armHeight -
          arcLength;

        x = radius;
        y = armHeight - rightDistance;
        rotation = 180;
      }

      item.el.style.transform =
        `translate(-50%, -50%) ` +
        `translate(${x}px, ${y}px) ` +
        `rotate(${rotation}deg)`;

      item.el.style.zIndex = i;
    });
  }

  function startShuffleThenFan(deckItems, mode5){
    fanWrap.style.display = 'flex';
    fanStage.innerHTML = '';
    fanStage.classList.add('shuffling');

    deckHint.textContent =
      '正在洗牌，請稍候……';

    drawnRow.innerHTML = '';

    revealDetail.innerHTML = '';
    revealDetail.classList.remove('active');

    drawnCount = 0;
    collectedResults = [];

    fanItems = deckItems.map(d => ({
      ...d,
      el: null
    }));

    setTimeout(() => {
      fanStage.classList.remove('shuffling');

      fanItems.forEach(item => {
        const el =
          document.createElement('div');

        el.className = 'fan-card';

        fanStage.appendChild(el);
        item.el = el;
      });

      layoutFan();

      if(mode5){
        deckHint.textContent =
          '點擊扇形中任一張牌，感應你的指示牌位置';

        fanItems.forEach(item => {
          item.el.addEventListener(
            'click',
            () => revealMode5()
          );
        });

      }else{
        deckHint.textContent =
          `依序點擊卡牌，抽出第 1 張（共需 ${drawPlan.length} 張）`;

        fanItems.forEach(item => {
          item.el.addEventListener(
            'click',
            () => drawStandardCard(item)
          );
        });
      }
    }, 900);
  }

  function flipCardInPlace(item, label){
    item.el.classList.add('revealed');

    item.el.innerHTML = `
      <img
        src="${item.card.image_url}"
        alt="${item.card.name}"
      >
      <div class="mini-cap">
        ${item.card.name}
      </div>
    `;
  }

  function drawStandardCard(item){
    if(
      item.el.classList.contains('revealed') ||
      item.el.classList.contains('dimmed')
    ){
      return;
    }

    if(drawnCount >= drawPlan.length){
      return;
    }

    const label = drawPlan[drawnCount];

    flipCardInPlace(item, label);
    renderDrawnCard(label, item.card);
    appendDetail(label, item.card);

    collectedResults.push({
      label,
      card: item.card
    });

    drawnCount++;

    if(drawnCount >= drawPlan.length){
      deckHint.textContent =
        '解讀完成 ✦ 願這份訊息與你同在';

      fanItems.forEach(i => {
        if(!i.el.classList.contains('revealed')){
          i.el.classList.add('dimmed');
        }
      });

      finishAndSend();

    }else{
      deckHint.textContent =
        `依序點擊卡牌，抽出第 ${drawnCount + 1} 張（共需 ${drawPlan.length} 張）`;
    }
  }

  function revealMode5(){
    if(drawnCount > 0){
      return;
    }

    drawnCount = 1;

    const idx =
      fanItems.findIndex(i => i.isIndicator);

    const leftIdx = idx - 1;
    const rightIdx = idx + 1;

    fanItems.forEach((item, i) => {
      if(
        i === idx ||
        i === leftIdx ||
        i === rightIdx
      ){
        item.el.classList.add('spotlight');
      }else{
        item.el.classList.add('dimmed');
      }
    });

    deckHint.textContent =
      `「${selectedIndicatorName}」指示牌現身，為你點出主題……`;

    const indicatorItem = fanItems[idx];

    flipCardInPlace(
      indicatorItem,
      '指示牌'
    );

    renderDrawnCard(
      '指示牌',
      indicatorItem.card
    );

    appendDetail(
      '指示牌',
      indicatorItem.card
    );

    collectedResults.push({
      label: '指示牌',
      card: indicatorItem.card
    });

    setTimeout(() => {
      deckHint.textContent =
        '正在揭示左右兩側的精油指引……';

      const revealSide = (
        sideIdx,
        label,
        delay
      ) => {
        setTimeout(() => {
          if(
            sideIdx < 0 ||
            sideIdx >= fanItems.length
          ){
            return;
          }

          const sideItem =
            fanItems[sideIdx];

          flipCardInPlace(
            sideItem,
            label
          );

          renderDrawnCard(
            label,
            sideItem.card
          );

          appendDetail(
            label,
            sideItem.card
          );

          collectedResults.push({
            label,
            card: sideItem.card
          });
        }, delay);
      };

      revealSide(
        leftIdx,
        `「${selectedIndicatorName}」左側提升精油`,
        0
      );

      revealSide(
        rightIdx,
        `「${selectedIndicatorName}」右側提升精油`,
        500
      );

      setTimeout(() => {
        deckHint.textContent =
          '解讀完成 ✦ 願這份訊息與你同在';

        finishAndSend();
      }, 1100);
    }, 900);
  }

  function renderDrawnCard(label, card){
    const slot =
      document.createElement('div');

    slot.className = 'drawn-slot';

    slot.innerHTML = `
      <div class="slot-label">
        ${label}
      </div>

      <div class="drawn-card">
        <img
          src="${card.image_url}"
          alt="${card.name}"
        >

        <div class="cap">
          <b>${card.name}</b>
          <span>${card.name_en || ''}</span>
        </div>
      </div>
    `;

    drawnRow.appendChild(slot);
  }

  function appendDetail(label, card){
    const el =
      document.createElement('div');

    el.className = 'detail-card';

    el.innerHTML = `
      <div class="dc-label">
        ${label}
      </div>

      <div class="dc-name">
        ${card.name}
      </div>

      <div class="dc-name-en">
        ${card.name_en || ''}
      </div>

      ${
        card.keywords
          ? `<div class="dc-keywords">${card.keywords}</div>`
          : ''
      }

      ${
        card.guidance
          ? `<div class="dc-guidance">${card.guidance}</div>`
          : ''
      }

      ${
        card.chakra
          ? `<div class="dc-chakra">脈輪：${card.chakra}</div>`
          : ''
      }
    `;

    revealDetail.appendChild(el);
    revealDetail.classList.add('active');
  }

  // 組 Flex carousel JSON，
  // 透過 liff.sendMessages() 送回 LINE 聊天室。
  function buildBubble(label, card){
    const bodyContents = [
      {
        type: "box",
        layout: "baseline",
        contents: [
          {
            type: "text",
            text: "關鍵詞",
            size: "xs",
            color: "#B08968",
            flex: 1
          },
          {
            type: "text",
            text: card.keywords || "無",
            size: "sm",
            color: "#555555",
            flex: 4,
            wrap: true
          },
        ],
      },
    ];

    if(card.chakra){
      bodyContents.unshift({
        type: "box",
        layout: "baseline",
        contents: [
          {
            type: "text",
            text: "脈輪",
            size: "xs",
            color: "#B08968",
            flex: 1
          },
          {
            type: "text",
            text: card.chakra,
            size: "sm",
            color: "#555555",
            flex: 4,
            wrap: true
          },
        ],
      });
    }

    bodyContents.push({
      type: "separator",
      margin: "md"
    });

    bodyContents.push({
      type: "text",
      text: card.guidance || "無",
      wrap: true,
      margin: "md",
      size: "sm",
      color: "#333333"
    });

    if(card.description){
      bodyContents.push({
        type: "separator",
        margin: "md"
      });

      bodyContents.push({
        type: "text",
        text: card.description,
        wrap: true,
        margin: "md",
        size: "xs",
        color: "#777777"
      });
    }

    return {
      type: "bubble",

      header: {
        type: "box",
        layout: "vertical",
        contents: [
          {
            type: "text",
            text: label,
            size: "xs",
            color: "#B08968",
            align: "center"
          },
          {
            type: "text",
            text: card.name,
            weight: "bold",
            size: "xl",
            align: "center"
          },
          {
            type: "text",
            text: card.name_en || "",
            size: "sm",
            align: "center",
            color: "#888888"
          },
        ],
      },

      hero: {
        type: "image",
        url: card.image_url,
        size: "full",
        aspectRatio: "4:3",
        aspectMode: "cover"
      },

      body: {
        type: "box",
        layout: "vertical",
        spacing: "sm",
        contents: bodyContents
      },
    };
  }

  function logDrawToBackend(){
    if(!collectedResults.length){
      return;
    }

    const payload = {
      user_id:
        liffProfile
          ? liffProfile.userId
          : '',

      display_name:
        liffProfile
          ? liffProfile.displayName
          : '',

      mode: `mode_${currentMode}`,

      cards:
        collectedResults.map(
          r => r.card.name
        ),
    };

    fetch(`${API_BASE}/api/log-draw`, {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json'
      },

      body: JSON.stringify(payload),

    }).catch(e => {
      console.error(
        '[log-draw error]',
        e
      );
    });
  }

  function finishAndSend(){
    showAgainButton();
    logDrawToBackend();

    if(
      !liffReady ||
      !window.liff ||
      !liff.isInClient()
    ){
      sendStatus.textContent =
        '（非 LINE 內開啟，結果僅顯示於本頁面）';

      return;
    }

    const bubbles =
      collectedResults.map(
        r => buildBubble(r.label, r.card)
      );

    const modeTitle =
      MODE_CONFIG[currentMode]
        ? MODE_CONFIG[currentMode].title
        : '指示牌';

    const altText =
      `${modeTitle}牌陣結果：` +
      collectedResults
        .map(r => r.card.name)
        .join('、');

    const flexMessage = {
      type: "flex",
      altText: altText,

      contents:
        bubbles.length > 1
          ? {
              type: "carousel",
              contents: bubbles
            }
          : bubbles[0],
    };

    sendStatus.textContent =
      '正在將結果送回聊天室……';

    liff.sendMessages([flexMessage])
      .then(() => {
        sendStatus.textContent =
          '已送回 LINE 聊天室 ✓ 即將自動關閉';

        setTimeout(() => {
          try{
            liff.closeWindow();
          }catch(e){}
        }, 1200);
      })
      .catch(err => {
        const reason =
          err && err.message
            ? err.message
            : String(err);

        sendStatus.textContent =
          `送回聊天室失敗：${reason}`;

        console.error(
          '[liff.sendMessages error]',
          err
        );
      });
  }

  function showAgainButton(){
    againBtn.style.display =
      'inline-block';
  }

  modeSelect.addEventListener(
    'click',
    e => {
      const btn =
        e.target.closest('.mode-btn');

      if(!btn){
        return;
      }

      enterStage(
        Number(btn.dataset.mode)
      );
    }
  );

  backBtn.addEventListener(
    'click',
    showModeSelect
  );

  againBtn.addEventListener(
    'click',
    showModeSelect
  );

  function initFromQuery(){
    const params =
      new URLSearchParams(
        window.location.search
      );

    const m =
      Number(params.get('mode'));

    if(m >= 1 && m <= 5){
      enterStage(m);
    }
  }

  function initLiff(){
    if(!window.liff){
      return Promise.resolve();
    }

    return liff
      .init({
        liffId: LIFF_ID
      })
      .then(() => {
        liffReady = true;

        if(
          liff.isLoggedIn &&
          liff.isLoggedIn()
        ){
          return liff
            .getProfile()
            .then(p => {
              liffProfile = p;
            })
            .catch(() => {});
        }
      })
      .catch(e => {
        console.error(
          '[liff.init error]',
          e
        );
      });
  }

  Promise
    .all([
      loadData(),
      initLiff()
    ])
    .then(() => {
      instruction.textContent = '';
      initFromQuery();
    })
    .catch(e => {
      console.error(
        '[loadData error]',
        e
      );

      instruction.textContent =
        '資料讀取失敗，請重新整理頁面再試一次。';
    });
})();