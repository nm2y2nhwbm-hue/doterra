(function(){
  "use strict";

  // ---------------------------------------------------------
  // TODO：Supabase 專案建好後，換成 Project Settings → API 裡的值
  // ---------------------------------------------------------
  const SUPABASE_URL = "https://qkcelwfjmahjjtfoiwlr.supabase.co";
  const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFrY2Vsd2ZqbWFoamp0Zm9pd2xyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY1MDg4MDksImV4cCI6MjEwMjA4NDgwOX0.vRVO6lzSTyn0znPDF6RI1s37tJuMEIvB-OUaZdJ-zr0";

  const SUPABASE_CONFIGURED =
    !SUPABASE_URL.includes("YOUR-PROJECT") && !SUPABASE_ANON_KEY.includes("YOUR-ANON");

  let _client = null;
  function getClient(){
    if (!SUPABASE_CONFIGURED || !window.supabase) return null;
    if (!_client) _client = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    return _client;
  }

  // 尚未設定 Supabase 時的本機備援碼（僅顯示用，不會真的保存到雲端）
  function localFallbackCode(){
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let code = '';
    for (let i = 0; i < 6; i++) code += chars[Math.floor(Math.random() * chars.length)];
    return 'INSIGHT-' + code;
  }

  // 儲存本次抽牌並取得專屬體驗碼
  // results: [{label, card_name, card_name_en, image_url}, ...]
  async function saveDrawAndGetCode(mode, results, lineUserId, lineDisplayName){
    const client = getClient();
    if (!client) return { code: localFallbackCode(), persisted: false };
    try {
      const { data, error } = await client.rpc('save_draw', {
        p_mode: mode,
        p_results: results,
        p_line_user_id: lineUserId || null,
        p_line_display_name: lineDisplayName || null,
      });
      if (error) throw error;
      return { code: data, persisted: true };
    } catch (e) {
      console.error('[saveDrawAndGetCode error]', e);
      return { code: localFallbackCode(), persisted: false };
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

  window.OracleSupabase = { SUPABASE_CONFIGURED, SUPABASE_URL, getClient, saveDrawAndGetCode, createBooking };
})();
