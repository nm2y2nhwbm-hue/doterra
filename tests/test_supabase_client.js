const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'static', 'supabase-client.js'),
  'utf8',
);

const requests = [];
const response = (ok, body) => ({
  ok,
  json: async () => body,
});

const context = {
  console: { error() {} },
  fetch: async (url, options = {}) => {
    requests.push({ url, options });
    if (url.endsWith('/health')) return response(true, { status: 'ready' });
    if (url.endsWith('/redeem')) {
      return response(true, {
        persisted: true,
        line_verified: true,
        code: 'INSIGHT-ABC234',
        mode: 1,
        results: [],
      });
    }
    return response(true, {
      persisted: true,
      line_verified: false,
      handoff_token: 'A'.repeat(43),
      expires_in: 600,
    });
  },
  window: {
    supabase: {
      createClient: (url, key) => ({
        url,
        key,
        rpc: async () => ({ data: 'RCPT-001', error: null }),
      }),
    },
  },
};

vm.runInNewContext(source, context, { filename: 'supabase-client.js' });

(async () => {
  const oracle = context.window.OracleSupabase;

  assert.match(oracle.SUPABASE_PUBLISHABLE_KEY, /^sb_publishable_/);
  assert.equal(oracle.SUPABASE_ANON_KEY, oracle.SUPABASE_PUBLISHABLE_KEY);
  assert.equal(oracle.getClient().key, oracle.SUPABASE_PUBLISHABLE_KEY);

  const readiness = await oracle.getDrawApiReadiness();
  assert.equal(readiness.ready, true);
  assert.equal(readiness.status, 'ready');
  assert.equal(requests[0].options.method, 'GET');

  const browserDraw = await oracle.saveDrawAndGetCode(1, [], null);
  assert.equal(browserDraw.persisted, true);
  assert.equal(browserDraw.lineVerified, false);
  assert.equal(browserDraw.code, null);
  assert.equal(browserDraw.handoffToken, 'A'.repeat(43));

  const redeemed = await oracle.redeemDrawHandoff('A'.repeat(43), 'id-token');
  assert.equal(redeemed.lineVerified, true);
  assert.equal(redeemed.code, 'INSIGHT-ABC234');

  const booking = await oracle.createBooking({ name: 'test' });
  assert.equal(booking.persisted, true);
  assert.equal(booking.receiptNo, 'RCPT-001');

  console.log('supabase-client tests passed');
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
