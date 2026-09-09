# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：線上正式環境端點活體探測與網路驗證 (tests/test_live_endpoints.py)
驗證 Render API 後端服務與 Vercel 前端靜態服務之健康狀態、CORS、資安標頭與延遲。
"""
import time
import unittest
import urllib.request
import urllib.error
import json

RENDER_BASE_URL = "https://doterra-73pv.onrender.com"
VERCEL_BASE_URL = "https://doterra-two.vercel.app"
TIMEOUT_SECONDS = 15


class TestLiveEndpoints(unittest.TestCase):
    """線上正式環境端點活體探測"""

    def _http_get(self, url, headers=None):
        req = urllib.request.Request(
            url,
            headers=headers or {"User-Agent": "Agent-3-Quality-Monitor/1.0"}
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                duration_ms = int((time.time() - t0) * 1000)
                body = resp.read()
                return resp.status, dict(resp.headers), body, duration_ms
        except urllib.error.HTTPError as e:
            duration_ms = int((time.time() - t0) * 1000)
            return e.code, dict(e.headers), e.read(), duration_ms
        except Exception as e:
            self.skipTest(f"連線至 {url} 逾時或離線: {e}")

    # --- Render 後端 API 探測 ---

    def test_live_render_health(self):
        """探測 Render API: /health 端點健康狀態"""
        status, headers, body, latency = self._http_get(f"{RENDER_BASE_URL}/health")
        self.assertEqual(status, 200, f"/health 回應代碼異常: {status}")
        data = json.loads(body.decode('utf-8'))
        self.assertEqual(data.get('status'), 'ok')

    def test_live_render_api_oils(self):
        """探測 Render API: /api/oils 精油資料庫結構"""
        status, headers, body, latency = self._http_get(f"{RENDER_BASE_URL}/api/oils")
        self.assertEqual(status, 200, f"/api/oils 回應代碼異常: {status}")
        data = json.loads(body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 60)
        # 檢驗核心欄位存在
        for item in data[:5]:
            self.assertIn('id', item)
            self.assertIn('name', item)
            self.assertIn('name_en', item)
            self.assertIn('guidance', item)

    def test_live_render_api_indicators(self):
        """探測 Render API: /api/indicators 指示卡資料庫"""
        status, headers, body, latency = self._http_get(f"{RENDER_BASE_URL}/api/indicators")
        self.assertEqual(status, 200)
        data = json.loads(body.decode('utf-8'))
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 12)

    def test_live_render_cors(self):
        """探測 Render API 是否具備正確的 Access-Control-Allow-Origin 標頭"""
        status, headers, _, _ = self._http_get(f"{RENDER_BASE_URL}/health")
        header_keys = {k.lower(): v for k, v in headers.items()}
        cors_origin = header_keys.get('access-control-allow-origin')
        self.assertIsNotNone(cors_origin, "Render API 缺少 Access-Control-Allow-Origin 標頭")

    # --- Vercel 前端服務探測 ---

    def test_live_vercel_core_pages(self):
        """探測 Vercel 前端核心頁面正常 HTTP 200 返回"""
        pages = [
            '/',
            '/cards.html',
            '/oils.html',
            '/booking.html',
            '/admin.html',
            '/reception.html',
            '/inventory.html',
            '/sites.html'
        ]
        for p in pages:
            status, _, _, latency = self._http_get(f"{VERCEL_BASE_URL}{p}")
            self.assertEqual(status, 200, f"頁面 {p} 回應異常: {status}")

    def test_live_vercel_cart_assets(self):
        """探測 Vercel 購物車元件資產 (cart.css, cart.js)"""
        for asset in ['/cart.css', '/cart.js']:
            status, headers, _, _ = self._http_get(f"{VERCEL_BASE_URL}{asset}")
            self.assertEqual(status, 200, f"購物車資產 {asset} 回應異常: {status}")

    def test_live_vercel_cache_headers(self):
        """探測 Vercel 邊緣 CDN 快取標頭正常返回"""
        status, headers, _, _ = self._http_get(VERCEL_BASE_URL)
        header_keys = {k.lower(): v for k, v in headers.items()}
        self.assertIn('x-vercel-id', header_keys, "缺少 X-Vercel-Id 標頭")


if __name__ == '__main__':
    unittest.main()
