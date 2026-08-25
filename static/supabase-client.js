(function(){
  "use strict";

  // 公開瀏覽器設定。publishable key 僅具有 anon 權限，可安全放在前端；
  // service-role / secret key 僅能存在 Render。
  const SUPABASE_URL = "https://qkcelwfjmahjjtfoiwlr.supabase.co";
  const SUPABASE_PUBLISHABLE_KEY = "sb_publishable_GjwIhE4HLg8LPCmOXn1ukA_2bL2w8lP";
  // 保留既有名稱，避免 booking.js / inventory.js 的相容介面中斷。
  const SUPABASE_ANON_KEY = SUPABASE_PUBLISHABLE_KEY;
  const DRAW_API_BASE = "https://doterra-73pv.onrender.com/api/draws";

  const SUPABASE_CONFIGURED =
    !SUPABASE_URL.includes("YOUR-PROJECT") &&
    !SUPABASE_PUBLISHABLE_KEY.includes("YOUR-PUBLISHABLE");

  let _client = null;
  function getClient(){
    if (!SUPABASE_CONFIGURED || !window.supabase) return null;
    if (!_client) _client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    return _client;
  }

  async function callDrawApi(path, payload){
    const response = await fetch(DRAW_API_BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || '抽牌保存服務暫時無法使用');
    return data;
  }

  async function getDrawApiReadiness(){
    try {
      const response = await fetch(DRAW_API_BASE + '/health', {
        method: 'GET',
        cache: 'no-store',
      });
      const data = await response.json().catch(() => ({}));
      return {
        ready: response.ok && data.status === 'ready',
        status: data.status || 'unavailable',
      };
    } catch (e) {
      return { ready: false, status: 'unavailable' };
    }
  }

  function normalizeDrawResponse(data){
    return {
      persisted: data.persisted === true,
      lineVerified: data.line_verified === true,
      code: typeof data.code === 'string' ? data.code : null,
      handoffToken: typeof data.handoff_token === 'string' ? data.handoff_token : null,
      expiresIn: Number(data.expires_in) || 0,
      mode: Number(data.mode) || null,
      results: Array.isArray(data.results) ? data.results : null,
    };
  }

  // 抽牌保存改由 Render 後端執行；瀏覽器不再直接呼叫匿名 save_draw RPC。
  // results: [{label, card_name, card_name_en, image_url}, ...]
  async function saveDrawAndGetCode(mode, results, lineIdToken){
    try {
      const data = await callDrawApi('', {
        mode,
        results,
        id_token: lineIdToken || null,
      });
      return normalizeDrawResponse(data);
    } catch (e) {
      console.error('[saveDrawAndGetCode error]', e);
      return { code: null, persisted: false, error: e.message || '抽牌結果尚未保存' };
    }
  }

  async function redeemDrawHandoff(handoffToken, lineIdToken){
    try {
      const data = await callDrawApi('/redeem', {
        handoff_token: handoffToken,
        id_token: lineIdToken,
      });
      return normalizeDrawResponse(data);
    } catch (e) {
      console.error('[redeemDrawHandoff error]', e);
      return { code: null, persisted: false, error: e.message || '抽牌交接失敗' };
    }
  }

  // 貴賓預約表單會用到（booking.html 尚未建立，先備好這支函式）
  async function createBooking(fields){
    const client = getClient();
    if (!client) return { receiptNo: null, persisted: false, error: 'Supabase 尚未設定' };
    try {
      const { data, error } = await client.rpc('create_booking', {
        p_draw_code: fields.drawCode || null,
        p_name: fields.name,
        p_email: fields.email || null,
        p_line_id: fields.lineId || null,
        p_booking_date: fields.bookingDate || null,
        p_main_concern: fields.mainConcern || null,
        p_mood: fields.mood || null,
        p_question: fields.question || null,
        p_note: fields.note || null,
      });
      if (error) throw error;
      return { receiptNo: data, persisted: true };
    } catch (e) {
      console.error('[createBooking error]', e);
      return { receiptNo: null, persisted: false, error: String(e.message || e) };
    }
  }

  window.OracleSupabase = {
    SUPABASE_CONFIGURED, SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY,
    SUPABASE_ANON_KEY, getClient, getDrawApiReadiness,
    saveDrawAndGetCode, redeemDrawHandoff, createBooking,
  };
})();
