// Supabase Edge Function: sync-inventory
// 從 Google 試算表（CSV 匯出，公開檢視連結，不需要 Google API 金鑰）同步進 oil_inventory。
//
// 部署方式：
//   supabase functions deploy sync-inventory
// 不需要額外設定 secrets，SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 是 Edge Function 內建可用的變數。
//
// 試算表欄位（照實際的表，第一列標題列，順序不拘）：
//   時間戳記, 產品編號, 精油名稱, 容量, 精油狀態, 開封日期, 有效日期, 備注
// 試算表裡「一列＝一瓶實體精油」，這支函式會依「精油名稱」分組彙總，
// 寫進 oil_inventory 時變成「一列＝一種精油的庫存彙總」：
//   quantity    = 該精油狀態不含「使用」字樣的瓶數（視為未開封／在庫）
//   in_use      = 該精油狀態含「使用」字樣的瓶數
//   expiry_date = 該精油所有瓶中最早的有效日期（最需要留意的那一瓶）
//   note        = 自動列出涵蓋的產品編號
//
// 分享設定要求：試算表要設成「知道連結的人都可以查看」

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const SHEET_ID = "10VsNYwMoPsZBE7wO5JdhdpEnZw7ldk1FWbT7X5JkrXA";
const CSV_URL = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv`;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const HEADER_MAP: Record<string, string> = {
  timestamp: "時間戳記",
  product_id: "產品編號",
  oil_name: "精油名稱",
  capacity: "容量",
  status: "精油狀態",
  opened_date: "開封日期",
  expiry_date: "有效日期",
  note: "備注",
};

function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++; }
        else inQuotes = false;
      } else field += c;
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ',') { row.push(field); field = ""; }
      else if (c === '\n') { row.push(field); rows.push(row); row = []; field = ""; }
      else if (c === '\r') { /* skip */ }
      else field += c;
    }
  }
  if (field.length || row.length) { row.push(field); rows.push(row); }
  return rows.filter(r => r.length > 1 || (r.length === 1 && r[0] !== ""));
}

// 把常見的日期格式（含中文年月日、YYYY/MM/DD）轉成 YYYY-MM-DD，轉不了就回傳 null
function normalizeDate(raw: string | undefined): string | null {
  if (!raw) return null;
  const s = raw.trim();
  if (!s) return null;
  const iso = s.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})/);
  if (iso) return `${iso[1]}-${iso[2].padStart(2, "0")}-${iso[3].padStart(2, "0")}`;
  const cn = s.match(/^(\d{4})年(\d{1,2})月(\d{1,2})日?/);
  if (cn) return `${cn[1]}-${cn[2].padStart(2, "0")}-${cn[3].padStart(2, "0")}`;
  return null;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS_HEADERS });

  try {
    const authHeader = req.headers.get("Authorization") || "";
    const token = authHeader.replace(/^Bearer\s+/i, "").trim();

    if (!token) {
      return new Response(
        JSON.stringify({ ok: false, error: "未提供認證憑證 (Missing Authorization header)" }),
        { status: 401, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } },
      );
    }

    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    // 1. 驗證呼叫者的 JWT 是否有效
    const { data: { user }, error: userErr } = await supabase.auth.getUser(token);
    if (userErr || !user) {
      return new Response(
        JSON.stringify({ ok: false, error: "身分驗證失敗：登入已過期或憑證無效" }),
        { status: 401, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } },
      );
    }

    // 2. 查驗呼叫者是否存在於 admins 白名單資料表
    const { data: adminRow, error: adminErr } = await supabase
      .from("admins")
      .select("user_id")
      .eq("user_id", user.id)
      .maybeSingle();

    if (adminErr || !adminRow) {
      return new Response(
        JSON.stringify({ ok: false, error: "權限不足：僅限管理員帳號執行庫存同步" }),
        { status: 403, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } },
      );
    }

    const csvRes = await fetch(CSV_URL);
    if (!csvRes.ok) {
      throw new Error(`無法讀取試算表 (HTTP ${csvRes.status})，請確認分享設定為「知道連結的人都可以查看」`);
    }
    const csvText = await csvRes.text();
    const rows = parseCsv(csvText);
    if (!rows.length) throw new Error("試算表是空的");

    const [header, ...dataRows] = rows;
    const idx: Record<string, number> = {};
    for (const key of Object.keys(HEADER_MAP)) {
      idx[key] = header.indexOf(HEADER_MAP[key]);
    }
    if (idx.oil_name === -1) {
      throw new Error(`試算表標題列缺少「${HEADER_MAP.oil_name}」欄位，請確認第一列欄位名稱`);
    }

    // 依精油名稱分組彙總（產品編號固定一個，取該精油第一次出現的值即可）
    const groups = new Map<string, {
      product_id: string | null; quantity: number; in_use: number;
      capacity: string | null; expiry_date: string | null;
    }>();

    for (const r of dataRows) {
      const oilName = idx.oil_name >= 0 ? (r[idx.oil_name] || "").trim() : "";
      if (!oilName) continue;

      const status = idx.status >= 0 ? (r[idx.status] || "").trim() : "";
      const capacity = idx.capacity >= 0 ? (r[idx.capacity] || "").trim() : "";
      const expiry = normalizeDate(idx.expiry_date >= 0 ? r[idx.expiry_date] : undefined);
      const productId = idx.product_id >= 0 ? (r[idx.product_id] || "").trim() : "";

      if (!groups.has(oilName)) {
        groups.set(oilName, { product_id: null, quantity: 0, in_use: 0, capacity: null, expiry_date: null });
      }
      const g = groups.get(oilName)!;

      if (status.includes("使用")) g.in_use++;
      else g.quantity++;

      if (!g.product_id && productId) g.product_id = productId;
      if (!g.capacity && capacity) g.capacity = capacity;
      if (expiry && (!g.expiry_date || expiry < g.expiry_date)) g.expiry_date = expiry;
    }

    let inserted = 0, updated = 0;
    for (const [oilName, g] of groups.entries()) {
      const item = {
        product_id: g.product_id,
        oil_name: oilName,
        quantity: g.quantity,
        in_use: g.in_use,
        unit: "瓶",
        capacity: g.capacity,
        expiry_date: g.expiry_date,
      };

      const { data: existing } = await supabase
        .from("oil_inventory")
        .select("id")
        .eq("oil_name", oilName)
        .maybeSingle();

      if (existing) {
        await supabase.from("oil_inventory").update(item).eq("id", existing.id);
        updated++;
      } else {
        await supabase.from("oil_inventory").insert(item);
        inserted++;
      }
    }

    return new Response(
      JSON.stringify({ ok: true, oilTypes: groups.size, rows: dataRows.length, inserted, updated }),
      { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } },
    );
  } catch (e) {
    return new Response(
      JSON.stringify({ ok: false, error: String((e as Error).message || e) }),
      { status: 400, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } },
    );
  }
});
