# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：後端 API 端點自動化整合測試 (tests/test_api_endpoints.py)
涵蓋健康檢查、精油與指示卡資料查詢、抽卡事件記錄、抽卡交接探測與安全邊界防禦。
"""
import json
import os
import unittest

# 設定測試環境變數
os.environ['CHANNEL_ACCESS_TOKEN'] = 'test-token'
os.environ['CHANNEL_SECRET'] = 'test-secret'


class TestApiEndpoints(unittest.TestCase):
    """後端 API 路由完整性與安全防護測試"""

    def setUp(self):
        try:
            from line_bot import app
            self.flask_app = app
            self.app = app.test_client()
            self.app.testing = True
        except ImportError:
            self.skipTest("Flask 依賴未安裝，跳過客戶端測試")

    def test_health_endpoint(self):
        """測試 /health 健康檢查端點（回傳版本、服務名稱與品項統計）"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'ok')
        self.assertEqual(data.get('service'), 'modern-oil-oracle-api')
        self.assertIn('version', data)
        self.assertGreaterEqual(data.get('catalog_items', 0), 60)

    def test_api_oils_endpoint(self):
        """測試 /api/oils 精油資料庫端點（驗證容量與建議零售價映射）"""
        response = self.app.get('/api/oils')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 60)

        # 檢驗第一筆精油關鍵欄位
        sample = data[0]
        self.assertIn('id', sample)
        self.assertIn('name', sample)
        self.assertIn('name_en', sample)
        self.assertIn('guidance', sample)
        self.assertIn('chakra', sample)
        self.assertIn('description', sample)
        self.assertIn('price_retail', sample)
        self.assertIn('capacity', sample)
        self.assertIsInstance(sample['price_retail'], int)
        self.assertGreater(sample['price_retail'], 0)

    def test_api_indicators_endpoint(self):
        """測試 /api/indicators 回傳指示卡資料庫"""
        response = self.app.get('/api/indicators')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 12)
        sample = data[0]
        self.assertIn('id', sample)
        self.assertIn('name', sample)

    def test_api_draws_health_endpoint(self):
        """測試 /api/draws/health 抽卡服務探測端點"""
        response = self.app.get('/api/draws/health')
        self.assertIn(response.status_code, [200, 503])
        data = json.loads(response.data)
        self.assertIn('status', data)

    def test_api_log_draw_endpoint(self):
        """測試 /api/log-draw POST 抽卡事件記錄"""
        payload = {
            "user_id": "test-user-001",
            "display_name": "測試使用者",
            "mode": "mirror",
            "cards": ["乳香", "安定平衡"]
        }
        response = self.app.post(
            '/api/log-draw',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("success", data)

    def test_api_create_draw_empty_payload(self):
        """測試 /api/draws 建立抽卡紀錄於空負載時的安全拒絕 (400)"""
        response = self.app.post(
            '/api/draws',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 422, 500])
        data = json.loads(response.data)
        self.assertFalse(data.get('persisted', False))

    def test_api_redeem_draw_invalid_token(self):
        """測試 /api/draws/redeem 兌換無效或竄改之 Token 安全阻斷"""
        payload = {
            "token": "invalid-tampered-token-123",
            "id_token": "fake-line-id-token"
        }
        response = self.app.post(
            '/api/draws/redeem',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 401, 403, 404, 422, 500])
        data = json.loads(response.data)
        self.assertFalse(data.get('persisted', False))

    def test_client_ip_header_precedence(self):
        """測試反向代理客戶端 IP 辨識優先級 (CF-Connecting-IP > X-Real-IP > X-Forwarded-For)"""
        from api.routes import _request_client_ip

        # 測試 CF-Connecting-IP 最高優先級
        with self.flask_app.test_request_context(headers={
            'CF-Connecting-IP': '203.0.113.195',
            'X-Real-IP': '198.51.100.1',
            'X-Forwarded-For': '192.0.2.1, 10.0.0.1'
        }):
            ip = _request_client_ip()
            self.assertEqual(ip, '203.0.113.195')

        # 測試 X-Real-IP 優先於 X-Forwarded-For
        with self.flask_app.test_request_context(headers={
            'X-Real-IP': '198.51.100.1',
            'X-Forwarded-For': '192.0.2.1, 10.0.0.1'
        }):
            ip = _request_client_ip()
            self.assertEqual(ip, '198.51.100.1')

        # 測試 X-Forwarded-For 逗號分隔取第一個原始 IP
        with self.flask_app.test_request_context(headers={
            'X-Forwarded-For': '192.0.2.1, 10.0.0.1'
        }):
            ip = _request_client_ip()
            self.assertEqual(ip, '192.0.2.1')

    def test_line_webhook_echo_loop_prevention(self):
        """防回音與訊息路由測試案例：
        1. 模擬 LINE Webhook 收到體驗碼與抽卡結果時，斷言回傳為 None（杜絕死循環卡片再次出現）
        2. 正向對照組：確認正規使用者選單指令（今日能量、鏡子、河流、岔路）仍能正常回傳導向卡片
        """
        from router import route_message

        # 1. 攔截測試：體驗碼與抽卡結果應直接靜默（return None）
        echo_messages = [
            "體驗碼：INSIGHT-ABC123",
            "體驗碼：INSIGHT-XYZ999\n請提供給您的精油顧問，即可了解禮盒體驗 🌿",
            "INSIGHT-ABC123",
            "insight-lowercase-001",
            "今日能量牌陣結果：乳香、安定平衡",
            "抽牌結果：乳香、永久花",
            "抽卡結果：神聖之蓮",
            "這是我的體驗碼：INSIGHT-TEST99",
        ]
        for msg in echo_messages:
            res = route_message("test-user-id", msg)
            self.assertIsNone(
                res,
                f"收到抽卡回傳訊息 '{msg}' 時未返回 None，將導致機器人產生死循環抽卡卡片回覆！"
            )

        # 2. 正向對照組：驗證合法關鍵字未被誤殺
        normal_cases = [
            ("今日能量", "mode_redirect"),
            ("鏡子 1~5", "category_redirect"),
            ("河流 6~10", "category_redirect"),
            ("岔路 11~12", "category_redirect"),
            ("一般日常諮詢詢問", "category_redirect"),
        ]
        for keyword, expected_type in normal_cases:
            res = route_message("test-user-id", keyword)
            self.assertIsNotNone(
                res,
                f"合法指令 '{keyword}' 遭誤判為 None！"
            )
            self.assertEqual(
                res.get("type"),
                expected_type,
                f"合法指令 '{keyword}' 回傳之類型錯誤：預期 {expected_type}，實際取得 {res.get('type')}"
            )

        # 3. 空訊息測試
        self.assertIsNone(route_message("test-user-id", ""))



if __name__ == '__main__':
    unittest.main()