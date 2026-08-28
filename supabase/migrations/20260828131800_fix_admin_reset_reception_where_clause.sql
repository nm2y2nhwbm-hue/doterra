-- =========================================================
-- 修復管理員接待處全部歸零（補齊 WHERE true 避免 safeupdate 攔截）
-- 檔案：20260828131800_fix_admin_reset_reception_where_clause.sql
-- =========================================================

create or replace function public.admin_reset_reception()
returns jsonb
language plpgsql
security definer
set search_path = ''
as \$\$
declare
  deleted_bookings integer := 0;
  deleted_draws integer := 0;
  deleted_counters integer := 0;
begin
  -- 權限檢查：僅允許白名單內的管理員執行
  if (select auth.uid()) is null or not exists (
    select 1
    from public.admins
    where admins.user_id = (select auth.uid())
  ) then
    raise exception 'administrator permission required' using errcode = '42501';
  end if;

  -- 1. 先清除預約資料（加上 where true 符合 safeupdate 規範）
  delete from public.bookings where true;
  get diagnostics deleted_bookings = row_count;

  -- 2. 清除抽牌紀錄
  delete from public.draws where true;
  get diagnostics deleted_draws = row_count;

  -- 3. 重設受付編號計數器
  delete from public.booking_counters where true;
  get diagnostics deleted_counters = row_count;

  return jsonb_build_object(
    'bookings', deleted_bookings,
    'draws', deleted_draws,
    'counters', deleted_counters
  );
end;
\$\$;

grant execute on function public.admin_reset_reception to authenticated;