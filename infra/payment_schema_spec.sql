-- ==============================================================================
-- 💳 Agent 5 維運與金流：線上支付資料庫 Schema 與 RLS 安全策略規格
-- 檔案位置: infra/payment_schema_spec.sql
-- 職責範圍: Agent 5 (維運與金流工程師)
-- 用途: 提供 Agent 1 (後端工程師) 與 Supabase 資料庫套用之訂單與金流稽核資料表結構
-- ==============================================================================

-- 1. 訂單主表 (orders)
CREATE TABLE IF NOT EXISTS public.orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no VARCHAR(64) UNIQUE NOT NULL,               -- 唯一訂單編號 (例如: ORD20260910XXXX)
    line_user_id VARCHAR(128) DEFAULT NULL,             -- LINE 用戶識別碼 (可為空，支援純網頁購買)
    customer_name VARCHAR(100) NOT NULL,                -- 訂購人姓名
    customer_email VARCHAR(255) DEFAULT NULL,           -- 電子郵件
    customer_phone VARCHAR(50) NOT NULL,                -- 聯絡電話 (取貨/通知用)
    shipping_address TEXT DEFAULT NULL,                 -- 配送地址
    items JSONB NOT NULL,                               -- 商品明細 [{"id":"30110302","name":"真正薰衣草","volume":"15ml","qty":1,"price":1160}]
    total_amount INTEGER NOT NULL CHECK (total_amount > 0), -- 訂單總額 (後端依 doterra.csv 重算)
    currency VARCHAR(10) DEFAULT 'TWD' NOT NULL,
    payment_method VARCHAR(32) NOT NULL,                -- 'ecpay_credit' | 'ecpay_atm' | 'ecpay_cvs' | 'line_pay'
    status VARCHAR(32) DEFAULT 'pending' NOT NULL,      -- 'pending' | 'paid' | 'failed' | 'cancelled' | 'refunded'
    trade_no VARCHAR(128) DEFAULT NULL,                 -- 金流商回傳之交易序號
    paid_at TIMESTAMPTZ DEFAULT NULL,                   -- 付款完成時間
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- 索引優化
CREATE INDEX IF NOT EXISTS idx_orders_order_no ON public.orders (order_no);
CREATE INDEX IF NOT EXISTS idx_orders_line_user_id ON public.orders (line_user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON public.orders (status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON public.orders (created_at DESC);

-- 2. 金流交易審計日誌表 (payment_logs)
CREATE TABLE IF NOT EXISTS public.payment_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no VARCHAR(64) NOT NULL,
    gateway VARCHAR(32) NOT NULL,                       -- 'ecpay' | 'line_pay'
    action_type VARCHAR(32) NOT NULL,                   -- 'checkout_request' | 'webhook_callback' | 'confirm_response'
    raw_payload JSONB NOT NULL,                         -- 原始 Webhook 回調或請求資料 (用於排錯與驗證)
    check_mac_status BOOLEAN DEFAULT TRUE NOT NULL,     -- 簽章驗算是否通過 (CheckMacValue 或 HMAC)
    client_ip VARCHAR(64) DEFAULT NULL,                 -- 金流通知伺服器來源 IP
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_payment_logs_order_no ON public.payment_logs (order_no);
CREATE INDEX IF NOT EXISTS idx_payment_logs_created_at ON public.payment_logs (created_at DESC);

-- ==============================================================================
-- 🔒 Row Level Security (RLS) 安全隔離策略
-- ==============================================================================

-- 啟用 RLS
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payment_logs ENABLE ROW LEVEL SECURITY;

-- 嚴禁匿名存取金流日誌
DROP POLICY IF EXISTS "Deny anon access to payment_logs" ON public.payment_logs;
CREATE POLICY "Deny anon access to payment_logs" ON public.payment_logs
    FOR ALL TO anon USING (false);

-- 僅限管理員帳號讀取金流日誌
DROP POLICY IF EXISTS "Admins can view payment_logs" ON public.payment_logs;
CREATE POLICY "Admins can view payment_logs" ON public.payment_logs
    FOR SELECT TO authenticated
    USING (
        auth.jwt() ->> 'email' IN (SELECT email FROM public.admins)
    );

-- 訂單主表：匿名用戶不可任意 SELECT 全部訂單 (防爬蟲個資外洩)
DROP POLICY IF EXISTS "Anon cannot list all orders" ON public.orders;
CREATE POLICY "Anon cannot list all orders" ON public.orders
    FOR SELECT TO anon USING (false);

-- 管理員可查閱與管理所有訂單
DROP POLICY IF EXISTS "Admins can manage all orders" ON public.orders;
CREATE POLICY "Admins can manage all orders" ON public.orders
    FOR ALL TO authenticated
    USING (
        auth.jwt() ->> 'email' IN (SELECT email FROM public.admins)
    );
