-- =========================================================
-- 多特瑞精油洞悉卡｜LOG5 網站管理中心 資料庫設定
-- 請在 supabase_phase3_admin.sql 執行過（admins 表已存在）之後再執行這段
-- =========================================================

create or replace function get_db_health() returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_size bigint;
  v_size_pretty text;
  v_active int;
  v_max int;
begin
  if not exists (select 1 from admins where user_id = auth.uid()) then
    raise exception '權限不足';
  end if;

  select pg_database_size(current_database()) into v_size;
  select pg_size_pretty(v_size) into v_size_pretty;
  select count(*) into v_active from pg_stat_activity where datname = current_database();
  select setting::int into v_max from pg_settings where name = 'max_connections';

  return jsonb_build_object(
    'db_size_bytes', v_size,
    'db_size_pretty', v_size_pretty,
    'active_connections', v_active,
    'max_connections', v_max
  );
end;
$$;

grant execute on function get_db_health to authenticated;
-- 注意：權限檢查寫在函式內部（只有 admins 白名單成員能拿到資料），
-- 所以就算 grant 給整個 authenticated 角色也不會外洩給非管理員的登入帳號。
