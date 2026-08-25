-- Keep trigger dependencies resolvable when callers use an empty search_path.
-- The secure backend RPC intentionally sets search_path = '', so every
-- application object referenced by this trigger must be schema-qualified.

create or replace function public.set_draw_code() returns trigger
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
      exit when not exists (
        select 1
        from public.draws
        where code = candidate
      ) or tries > 10;
      tries := tries + 1;
    end loop;
    new.code := candidate;
  end if;
  return new;
end;
$$;
