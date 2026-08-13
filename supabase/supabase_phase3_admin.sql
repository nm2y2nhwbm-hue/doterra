-- =========================================================
-- 多特瑞精油洞悉卡｜Phase 3 管理後台 資料庫設定
-- 請先完成「建立管理員登入帳號」再執行這段 SQL（見下方說明）
-- =========================================================

-- ---------------------------------------------------------
-- 0. 事前準備（一次性，在 Supabase 後台操作，不是 SQL）：
--    Authentication → Users → Add user，建立你要用來登入管理後台的
--    Email + 密碼帳號。建立好之後，把該使用者的 UUID（User UID 欄位）
--    複製下來，等一下要用在下面的 insert 裡。
--
--    注意：Supabase 預設允許任何人自行註冊帳號。如果只靠「已登入」
--    就給資料讀取權限，等於任何路人註冊帳號都能看到所有預約人資料。
--    所以這裡改用「白名單表」的做法——只有出現在 admins 表裡的
--    使用者，RLS 才會放行，其他登入帳號一律看不到任何資料。
-- ---------------------------------------------------------

create table if not exists admins (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

alter table admins enable row level security;

-- 讓已登入使用者可以查詢「自己是不是 admin」（前端登入後會用這個判斷要不要放行進後台）
create policy "self can check own admin row" on admins
  for select to authenticated
  using (user_id = auth.uid());

-- ---------------------------------------------------------
-- 1. bookings / draws 開放給白名單內的 admin 讀取（與更新處理狀態）
-- ---------------------------------------------------------
drop policy if exists "admin can select bookings" on bookings;
create policy "admin can select bookings" on bookings
  for select to authenticated
  using (exists (select 1 from admins where user_id = auth.uid()));

drop policy if exists "admin can update bookings" on bookings;
create policy "admin can update bookings" on bookings
  for update to authenticated
  using (exists (select 1 from admins where user_id = auth.uid()))
  with check (exists (select 1 from admins where user_id = auth.uid()));

drop policy if exists "admin can select draws" on draws;
create policy "admin can select draws" on draws
  for select to authenticated
  using (exists (select 1 from admins where user_id = auth.uid()));

-- ---------------------------------------------------------
-- 2. 最後一步：把你在步驟 0 複製的 UUID 貼進來，執行這一行
--    （可以重複執行多次，加入多位管理員）
-- ---------------------------------------------------------
-- insert into admins(user_id) values ('貼上你的-使用者-UUID') on conflict do nothing;
