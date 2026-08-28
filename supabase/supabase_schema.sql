-- =========================================================
-- 多特瑞精油洞悉卡｜Phase 2 資料庫結構（Supabase / Postgres）
-- 使用方式：Supabase 專案 → SQL Editor → 貼上整段執行一次即可
-- =========================================================

create extension if not exists pgcrypto;

-- ---------------------------------------------------------
-- 1. draws：每一次完整抽牌，結束時自動產生「專屬體驗碼」
--    （對應畫面上的 INSIGHT-4CFA3O）
-- ---------------------------------------------------------
create table if not exists draws (
  id                 uuid primary key default gen_random_uuid(),
  code               text unique,                 -- 專屬體驗碼，格式 INSIGHT-XXXXXX
  mode               int not null,                 -- 1~5，對應牌陣模式
  results            jsonb not null,                -- [{label, card_name, card_name_en, image_url}, ...]
  line_user_id       text,
  line_display_name  text,
  created_at         timestamptz not null default now()
);

-- 產生 6 碼體驗碼（避開易混淆字元 0/O/1/I）
create or replace function generate_draw_code() returns text
language plpgsql as $$
declare
  chars  text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  result text := '';
  i      int;
begin
  for i in 1..6 loop
    result := result || substr(chars, floor(random() * length(chars))::int + 1, 1);
  end loop;
  return 'INSIGHT-' || result;
end;
$$;

-- 新增 draws 資料列時，若沒帶 code 就自動產生（並確保不重複）
create or replace function set_draw_code() returns trigger
language plpgsql
set search_path = ''
as $$
declare
  candidate text;
  tries     int := 0;
begin
  if new.code is null then
    loop
      candidate := public.generate_draw_code();
      exit when not exists (select 1 from public.draws where code = candidate) or tries > 10;
      tries := tries + 1;
    end loop;
    new.code := candidate;
  end if;
  return new;
end;
$$;

drop trigger if exists trg_set_draw_code on draws;
create trigger trg_set_draw_code
  before insert on draws
  for each row execute function set_draw_code();

-- ---------------------------------------------------------
-- 2. bookings：貴賓體驗預約表單（下一步要做的 booking.html 會用到）
--    受付編號格式：TT20260812-003
-- ---------------------------------------------------------
create table if not exists bookings (
  receipt_no     text primary key,
  draw_code      text references draws(code),      -- 關聯到是哪一次抽牌結果來預約的（可為空）
  name           text not null,
  email          text,
  line_id        text,
  booking_date   date,
  main_concern   text,
  current_mood   text,
  question       text,
  note           text,
  status         text not null default '待處理',
  created_at     timestamptz not null default now()
);

create table if not exists booking_counters (
  day     date primary key,
  counter int not null default 0
);

create or replace function generate_receipt_no() returns text
language plpgsql as $$
declare
  today date := current_date;
  seq   int;
begin
  insert into booking_counters(day, counter) values (today, 1)
    on conflict (day) do update set counter = booking_counters.counter + 1
    returning counter into seq;
  return 'TT' || to_char(today, 'YYYYMMDD') || '-' || lpad(seq::text, 3, '0');
end;
$$;

create or replace function set_receipt_no() returns trigger
language plpgsql as $$
begin
  if new.receipt_no is null then
    new.receipt_no := generate_receipt_no();
  end if;
  return new;
end;
$$;

drop trigger if exists trg_set_receipt_no on bookings;
create trigger trg_set_receipt_no
  before insert on bookings
  for each row execute function set_receipt_no();

-- ---------------------------------------------------------
-- 3. RLS：全部鎖起來，anon 完全不能直接讀/寫資料表，
--    只能透過下面的 RPC 函式（security definer）操作，
--    這樣就不用煩惱 anon key 外洩會被拉走所有預約人資料。
-- ---------------------------------------------------------
alter table draws enable row level security;
alter table bookings enable row level security;
alter table booking_counters enable row level security;
-- 刻意不建立任何 policy = anon 對資料表完全無存取權限

-- ---------------------------------------------------------
-- 4. 表格資料完整性條件約束（Check Constraints）
-- ---------------------------------------------------------
alter table bookings
  add constraint chk_bookings_name_not_empty
  check (length(trim(name)) > 0 and length(name) <= 60);

alter table bookings
  add constraint chk_bookings_contact_required
  check (
    (email is not null and length(trim(email)) > 0)
    or
    (line_id is not null and length(trim(line_id)) > 0)
  );

alter table bookings
  add constraint chk_bookings_text_lengths
  check (
    length(coalesce(question, '')) <= 500
    and length(coalesce(note, '')) <= 500
  );

-- ---------------------------------------------------------
-- 5. RPC：線上預約建立函式（具備伺服器端嚴格校驗與防禦）
--    注意：舊版 save_draw 已廢棄（全面由 draw_handoffs 安全交接取代）
-- ---------------------------------------------------------
create or replace function public.create_booking(
  p_draw_code text default null,
  p_name text default null,
  p_email text default null,
  p_line_id text default null,
  p_booking_date date default null,
  p_main_concern text default null,
  p_mood text default null,
  p_question text default null,
  p_note text default null
) returns text
language plpgsql
security definer
set search_path = public
as $$
declare
  v_name         text := trim(coalesce(p_name, ''));
  v_email        text := nullif(trim(coalesce(p_email, '')), '');
  v_line_id      text := nullif(trim(coalesce(p_line_id, '')), '');
  v_main_concern text := nullif(trim(coalesce(p_main_concern, '')), '');
  v_mood         text := nullif(trim(coalesce(p_mood, '')), '');
  v_question     text := nullif(trim(coalesce(p_question, '')), '');
  v_note         text := nullif(trim(coalesce(p_note, '')), '');
  v_draw_code    text := nullif(trim(coalesce(p_draw_code, '')), '');
  v_receipt      text;
begin
  -- 伺服器端輸入校驗
  if v_name = '' then
    raise exception '請填寫姓名';
  end if;

  if length(v_name) > 60 then
    raise exception '姓名長度不可超過 60 個字元';
  end if;

  if v_email is null and v_line_id is null then
    raise exception '請至少填寫 Email 或 LINE ID 其中一項';
  end if;

  if v_email is not null and v_email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' then
    raise exception '請輸入正確格式的 Email 電子郵件信箱';
  end if;

  if p_booking_date is not null and p_booking_date < current_date then
    raise exception '預約日期不能早於今天';
  end if;

  if v_draw_code is not null and not exists (select 1 from public.draws where code = v_draw_code) then
    v_draw_code := null;
  end if;

  insert into public.bookings (
    draw_code,
    name,
    email,
    line_id,
    booking_date,
    main_concern,
    current_mood,
    question,
    note,
    status
  ) values (
    v_draw_code,
    v_name,
    v_email,
    v_line_id,
    p_booking_date,
    v_main_concern,
    v_mood,
    v_question,
    v_note,
    '待處理'
  )
  returning receipt_no into v_receipt;

  return v_receipt;
end;
$$;

grant execute on function public.create_booking to anon, authenticated, service_role;

-- ---------------------------------------------------------
-- 5. Phase 3（管理後台）要用的查詢權限，先留著不用管：
--    到時候後台會用 Supabase Auth 登入的 authenticated 角色，
--    另外開 select policy 給 authenticated，anon 依然完全看不到。
-- ---------------------------------------------------------
