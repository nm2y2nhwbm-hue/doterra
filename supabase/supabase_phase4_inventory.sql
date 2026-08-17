-- =========================================================
-- 多特瑞精油洞悉卡｜LOG2 精油庫存管理 資料庫設定
-- 請在 supabase_phase3_admin.sql 執行過（admins 表已存在）之後再執行這段
-- =========================================================

create table if not exists oil_inventory (
  id           uuid primary key default gen_random_uuid(),
  product_id   text,                          -- 產品編號（每種精油固定一個，像 SKU）
  oil_name     text not null unique,          -- 一列＝一種精油（彙總後的庫存），試算表裡同名的多瓶會合併成一列
  quantity     numeric not null default 0,    -- 庫存數量（未開封/在庫的瓶數）
  in_use       numeric not null default 0,    -- 使用中數量
  unit         text not null default '瓶',
  capacity     text,                          -- 容量，例如 15ml
  expiry_date  date,                          -- 有效期限（取該精油所有瓶中最早到期的一筆，最需要留意的日期）
  note         text,
  updated_at   timestamptz not null default now(),
  created_at   timestamptz not null default now()
);

-- 如果 oil_inventory 表是用更早版本建的，補上新欄位
alter table oil_inventory add column if not exists product_id text;

-- 如果 oil_inventory 表是用更早版本建的，補上 unique 限制方便 upsert
do $$ begin
  if not exists (select 1 from pg_constraint where conname = 'oil_inventory_oil_name_key') then
    alter table oil_inventory add constraint oil_inventory_oil_name_key unique (oil_name);
  end if;
end $$;

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
