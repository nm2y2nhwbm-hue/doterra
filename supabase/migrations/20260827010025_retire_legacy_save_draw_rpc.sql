-- =========================================================
-- 廢棄舊版 save_draw RPC（全面改用安全短效 handoff 憑證機制）
-- 檔案：20260827010025_retire_legacy_save_draw_rpc.sql
-- =========================================================

-- 撤銷匿名與一般登入使用者的執行權限
revoke execute on function public.save_draw(int, jsonb, text, text) from anon, authenticated, public;

-- 移除舊版未受保護的 save_draw 函式
drop function if exists public.save_draw(int, jsonb, text, text);