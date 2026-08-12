(() => {
  const siteToast = document.getElementById('site-toast');
  let toastTimer = null;

  function showToast(msg){
    if (!siteToast) return;
    siteToast.textContent = msg;
    siteToast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => siteToast.classList.remove('show'), 2400);
  }

  // 預約表單／受付編號／禮盒商城需串接後端（Phase 2），目前先提供明確提示，避免點了沒反應
  const bookBtn = document.getElementById('nav-book-btn');
  const heroGiftBtn = document.getElementById('hero-gift-btn');
  const barGiftBtn = document.getElementById('bar-gift-btn');

  if (bookBtn) bookBtn.addEventListener('click', () => showToast('貴賓預約功能即將上線，敬請期待 🌿'));
  if (heroGiftBtn) heroGiftBtn.addEventListener('click', () => showToast('體驗禮盒預約功能即將上線，敬請期待 🌿'));
  if (barGiftBtn) barGiftBtn.addEventListener('click', () => showToast('體驗禮盒預約功能即將上線，敬請期待 🌿'));
})();
