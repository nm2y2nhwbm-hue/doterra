# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：後端 API 端點自動化整合測試 (tests/test_api_endpoints.py)
"""
import unittest
import os
import json

# 設定測試環境變數
os.environ['CHANNEL_ACCESS_TOKEN'] = 'test-token'
os.environ['CHANNEL_SECRET'] = 'test-secret'


class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        try:
            from line_bot import app
            self.app = app.test_client()
            self.app.testing = True
        except ImportError:
            self.skipTest("Flask 依賴未安裝，跳過客戶端測試")

    def test_health_endpoint(self):
        """測試 /health 健康檢查端點"""
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data.get('status'), 'ok')

    def test_api_oils_endpoint(self):
        """測試 /api/oils 回傳精油資料庫"""
        response = self.app.get('/api/oils')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_api_indicators_endpoint(self):
        """測試 /api/indicators 回傳指示卡資料庫"""
        response = self.app.get('/api/indicators')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)


if __name__ == '__main__':
    unittest.main()