-- Cover the private handoff foreign key used during draw deletion and cleanup.
create index if not exists draw_handoffs_draw_id_idx
  on private.draw_handoffs (draw_id);
