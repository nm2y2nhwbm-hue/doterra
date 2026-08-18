-- 管理員可刪除 reception 預約；「完整歸零」會在同一交易中清除
-- bookings、draws 與 booking_counters。

do $$
begin
  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'bookings'
      and policyname = 'admin can delete bookings'
  ) then
    create policy "admin can delete bookings"
      on public.bookings
      for delete
      to authenticated
      using (
        exists (
          select 1
          from public.admins
          where admins.user_id = (select auth.uid())
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'draws'
      and policyname = 'admin can delete draws'
  ) then
    create policy "admin can delete draws"
      on public.draws
      for delete
      to authenticated
      using (
        exists (
          select 1
          from public.admins
          where admins.user_id = (select auth.uid())
        )
      );
  end if;

  if not exists (
    select 1
    from pg_policies
    where schemaname = 'public'
      and tablename = 'booking_counters'
      and policyname = 'admin can delete booking counters'
  ) then
    create policy "admin can delete booking counters"
      on public.booking_counters
      for delete
      to authenticated
      using (
        exists (
          select 1
          from public.admins
          where admins.user_id = (select auth.uid())
        )
      );
  end if;
end
$$;

create or replace function public.admin_reset_reception()
returns jsonb
language plpgsql
security invoker
set search_path = ''
as $$
declare
  deleted_bookings integer := 0;
  deleted_draws integer := 0;
  deleted_counters integer := 0;
begin
  if (select auth.uid()) is null or not exists (
    select 1
    from public.admins
    where admins.user_id = (select auth.uid())
  ) then
    raise exception 'administrator permission required' using errcode = '42501';
  end if;

  -- 外鍵 bookings.draw_code -> draws.code 沒有 ON DELETE CASCADE，
  -- 因此必須先刪 bookings，再刪 draws。
  delete from public.bookings;
  get diagnostics deleted_bookings = row_count;

  delete from public.draws;
  get diagnostics deleted_draws = row_count;

  delete from public.booking_counters;
  get diagnostics deleted_counters = row_count;

  return jsonb_build_object(
    'bookings', deleted_bookings,
    'draws', deleted_draws,
    'booking_counters', deleted_counters
  );
end;
$$;

-- 最小權限：匿名訪客不可直接刪表或呼叫管理 RPC；管理員仍由 RLS 白名單判斷。
revoke delete, truncate on public.bookings, public.draws, public.booking_counters from anon;
revoke truncate on public.bookings, public.draws, public.booking_counters from authenticated;
grant delete on public.bookings, public.draws, public.booking_counters to authenticated;

revoke execute on function public.admin_reset_reception() from public, anon;
grant execute on function public.admin_reset_reception() to authenticated;
