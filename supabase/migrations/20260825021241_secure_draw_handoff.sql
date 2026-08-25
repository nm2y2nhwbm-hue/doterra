-- Browser -> LINE/LIFF draw handoff.
-- This migration only adds the protected backend path. The legacy public
-- save_draw RPC is intentionally retired in a later deployment step, after
-- Render and Vercel have both switched to the backend API.

create schema if not exists private;
revoke all on schema private from public, anon, authenticated;

create table if not exists private.draw_handoffs (
  token_hash             text primary key check (token_hash ~ '^[0-9a-f]{64}$'),
  draw_id                uuid not null references public.draws(id) on delete cascade,
  expires_at             timestamptz not null,
  redeemed_at            timestamptz,
  redeemed_line_user_id  text,
  created_at             timestamptz not null default now()
);

create index if not exists draw_handoffs_expires_at_idx
  on private.draw_handoffs (expires_at);

alter table private.draw_handoffs enable row level security;
revoke all on private.draw_handoffs from public, anon, authenticated;

create table if not exists private.draw_request_limits (
  fingerprint     text primary key check (fingerprint ~ '^[0-9a-f]{64}$'),
  window_started  timestamptz not null default now(),
  request_count   integer not null default 1 check (request_count > 0)
);

create index if not exists draw_request_limits_window_started_idx
  on private.draw_request_limits (window_started);

alter table private.draw_request_limits enable row level security;
revoke all on private.draw_request_limits from public, anon, authenticated;

create or replace function public.backend_create_draw(
  p_mode integer,
  p_results jsonb,
  p_line_user_id text default null,
  p_line_display_name text default null,
  p_handoff_token_hash text default null,
  p_handoff_ttl_seconds integer default 600,
  p_request_fingerprint text default null
) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_draw_id uuid;
  v_code text;
  v_request_count integer;
  v_expected_result_count integer;
  v_ttl_seconds integer := greatest(60, least(coalesce(p_handoff_ttl_seconds, 600), 900));
begin
  if p_mode is null or p_mode < 1 or p_mode > 12 then
    raise exception 'invalid draw mode' using errcode = '22023';
  end if;

  v_expected_result_count := case p_mode
    when 1 then 1
    when 2 then 2
    when 3 then 3
    when 4 then 3
    when 5 then 3
    when 6 then 3
    when 7 then 3
    when 8 then 3
    when 9 then 3
    when 10 then 2
    when 11 then 4
    when 12 then 4
  end;

  if p_results is null
     or jsonb_typeof(p_results) <> 'array'
     or jsonb_array_length(p_results) <> v_expected_result_count then
    raise exception 'invalid draw results' using errcode = '22023';
  end if;

  if p_request_fingerprint is null
     or p_request_fingerprint !~ '^[0-9a-f]{64}$' then
    raise exception 'invalid request fingerprint' using errcode = '22023';
  end if;

  if p_handoff_token_hash is not null
     and p_handoff_token_hash !~ '^[0-9a-f]{64}$' then
    raise exception 'invalid handoff token hash' using errcode = '22023';
  end if;

  if (nullif(p_line_user_id, '') is null) = (p_handoff_token_hash is null) then
    raise exception 'draw must use exactly one verified delivery path' using errcode = '22023';
  end if;

  delete from private.draw_request_limits
  where window_started < now() - interval '1 day';

  insert into private.draw_request_limits(fingerprint, window_started, request_count)
  values (p_request_fingerprint, now(), 1)
  on conflict (fingerprint) do update
  set window_started = case
        when private.draw_request_limits.window_started < now() - interval '10 minutes'
          then now()
        else private.draw_request_limits.window_started
      end,
      request_count = case
        when private.draw_request_limits.window_started < now() - interval '10 minutes'
          then 1
        else private.draw_request_limits.request_count + 1
      end
  returning request_count into v_request_count;

  if v_request_count > 20 then
    return jsonb_build_object('rate_limited', true);
  end if;

  insert into public.draws(mode, results, line_user_id, line_display_name)
  values (
    p_mode,
    p_results,
    nullif(left(coalesce(p_line_user_id, ''), 128), ''),
    nullif(left(coalesce(p_line_display_name, ''), 100), '')
  )
  returning id, code into v_draw_id, v_code;

  if p_handoff_token_hash is not null then
    insert into private.draw_handoffs(token_hash, draw_id, expires_at)
    values (
      p_handoff_token_hash,
      v_draw_id,
      now() + make_interval(secs => v_ttl_seconds)
    );
  end if;

  return jsonb_build_object(
    'rate_limited', false,
    'code', v_code
  );
end;
$$;

create or replace function public.backend_redeem_draw_handoff(
  p_handoff_token_hash text,
  p_line_user_id text,
  p_line_display_name text default null
) returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_handoff private.draw_handoffs%rowtype;
  v_code text;
  v_mode integer;
  v_results jsonb;
begin
  if p_handoff_token_hash is null
     or p_handoff_token_hash !~ '^[0-9a-f]{64}$'
     or nullif(p_line_user_id, '') is null then
    return jsonb_build_object('status', 'invalid');
  end if;

  select * into v_handoff
  from private.draw_handoffs
  where token_hash = p_handoff_token_hash
  for update;

  if not found then
    return jsonb_build_object('status', 'invalid');
  end if;

  if v_handoff.expires_at <= now() then
    return jsonb_build_object('status', 'expired');
  end if;

  if v_handoff.redeemed_line_user_id is not null
     and v_handoff.redeemed_line_user_id <> p_line_user_id then
    return jsonb_build_object('status', 'used');
  end if;

  if v_handoff.redeemed_at is null then
    update private.draw_handoffs
    set redeemed_at = now(),
        redeemed_line_user_id = left(p_line_user_id, 128)
    where token_hash = p_handoff_token_hash;
  end if;

  update public.draws
  set line_user_id = left(p_line_user_id, 128),
      line_display_name = coalesce(
        nullif(left(coalesce(p_line_display_name, ''), 100), ''),
        line_display_name
      )
  where id = v_handoff.draw_id
    and (line_user_id is null or line_user_id = p_line_user_id);

  if not found then
    return jsonb_build_object('status', 'used');
  end if;

  select code, mode, results
  into v_code, v_mode, v_results
  from public.draws
  where id = v_handoff.draw_id;

  return jsonb_build_object(
    'status', 'ok',
    'code', v_code,
    'mode', v_mode,
    'results', v_results
  );
end;
$$;

revoke all on function public.backend_create_draw(integer, jsonb, text, text, text, integer, text)
  from public, anon, authenticated;
grant execute on function public.backend_create_draw(integer, jsonb, text, text, text, integer, text)
  to service_role;

revoke all on function public.backend_redeem_draw_handoff(text, text, text)
  from public, anon, authenticated;
grant execute on function public.backend_redeem_draw_handoff(text, text, text)
  to service_role;
