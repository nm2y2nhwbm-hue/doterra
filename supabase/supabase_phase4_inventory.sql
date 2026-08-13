-- =========================================================
-- 多特瑞精油洞悉卡｜LOG2 精油庫存管理 資料庫設定
-- 請在 supabase_phase3_admin.sql 執行過（admins 表已存在）之後再執行這段
-- =========================================================

create table if not exists oil_inventory (
  id           uuid primary key default gen_random_uuid(),
  oil_name     text not null,
  quantity     numeric not null default 0,   -- 目前庫存數量
  in_use       numeric not null default 0,   -- 使用中數量
  unit         text not null default '瓶',
  capacity     text,                          -- 容量，例如 15ml
  expiry_date  date,                          -- 有效期限
  note         text,
  updated_at   timestamptz not null default now(),
  created_at   timestamptz not null default now()
);

-- 更新資料列時自動刷新 updated_at
create or replace function touch_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_oil_inventory_touch on oil_inventory;
create trigger trg_oil_inventory_touch
  before update on oil_inventory
  for each row execute function touch_updated_at();

-- ---------------------------------------------------------
-- RLS：沿用跟 bookings/draws 一樣的 admins 白名單規則
-- ---------------------------------------------------------
alter table oil_inventory enable row level security;

drop policy if exists "admin can select inventory" on oil_inventory;
create policy "admin can select inventory" on oil_inventory
  for select to authenticated
  using (exists (select 1 from admins where user_id = auth.uid()));

drop policy if exists "admin can insert inventory" on oil_inventory;
create policy "admin can insert inventory" on oil_inventory
  for insert to authenticated
  with check (exists (select 1 from admins where user_id = auth.uid()));

drop policy if exists "admin can update inventory" on oil_inventory;
create policy "admin can update inventory" on oil_inventory
  for update to authenticated
  using (exists (select 1 from admins where user_id = auth.uid()))
  with check (exists (select 1 from admins where user_id = auth.uid()));

drop policy if exists "admin can delete inventory" on oil_inventory;
create policy "admin can delete inventory" on oil_inventory
  for delete to authenticated
  using (exists (select 1 from admins where user_id = auth.uid()));

-- Google 試算表同步之後再接：屆時會另外開一支 Edge Function 定期把試算表
-- 資料寫進這張表，寫入身分改用 service_role，不影響這裡的 anon/authenticated 規則。
