// 共用的分類與模式展示資料（標題／描述／所屬分類）
// index.html 的首頁選單、cards.html 的 script.js 都讀這份，避免兩邊文字各改各的。
window.CATEGORY_CATALOG = {
  mirror:    { name: '鏡子', icon: '鏡', eyebrow: 'MIRROR',    tagline: '照看你的此時此刻',       sub: '只映照當下，不推演過去與未來',       modes: [1,2,3,4,5] },
  river:     { name: '河流', icon: '河', eyebrow: 'RIVER',     tagline: '陪伴你的時間流動',       sub: '順著時間的脈絡，看見不同階段的自己', modes: [6,7,8,9,10] },
  crossroad: { name: '岔路', icon: '岔', eyebrow: 'CROSSROAD', tagline: '站在十字路口的香氣陪伴', sub: '在多個選項之間，先聽聽身體的聲音',   modes: [11,12] },
};

window.MODE_CATALOG = {
  1:  { title: '今日能量',               category: 'mirror',    desc: '單張心靈肯定小語' },
  2:  { title: '生活導引',               category: 'mirror',    desc: '現階段狀態與方向指引' },
  3:  { title: '三牌陣',                 category: 'mirror',    desc: '身・心・靈全方位深度解析' },
  4:  { title: '了解自我',               category: 'mirror',    desc: '別人眼中的你與真正的你' },
  5:  { title: '指示牌',                 category: 'mirror',    desc: '單一指示牌與精油對應占卜' },
  6:  { title: '主題時間流',             category: 'river',     desc: '選定主題卡，看過去成因與未來轉化' },
  7:  { title: '生命大運流年・看流年',    category: 'river',     desc: '回望前期、當下課題、展望後續' },
  8:  { title: '生命大運流年・看流月',    category: 'river',     desc: '月初、月中、月底的狀態變化' },
  9:  { title: '生命大運流年・看流日',    category: 'river',     desc: '稍早、此刻、稍晚的一日流動' },
  10: { title: '年度生命軌跡',           category: 'river',     desc: '純主題卡，看上下半年的重心位移' },
  11: { title: '二選一未來抉擇',         category: 'crossroad', desc: '兩個方案的當下心境與發展對照' },
  12: { title: '三選一十字路口',         category: 'crossroad', desc: '固定十字路口卡，盲抽三條岔路' },
};
