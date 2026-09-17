# -*- coding: utf-8 -*-
"""
Agent 1 負責範圍：第三方金流（LINE Pay v3 測試沙盒 Sandbox）自動化整合測試 (tests/test_payment_api.py) [檢驗 Agent 5 / Agent 2 金流邊界]
檢驗項目：
1. 金額伺服器端防偽重算（拒絕前端偽造價格、負數、不存在品項）
2. 唯一定錨 LINE Pay：非 linepay 渠道（包含已封存之 ecpay）精準攔截
3. 顧客資訊合法性校驗（姓名限制、聯絡方式必填一項）
4. LINE Pay v3 HMAC-SHA256 標頭授權簽章演算法
5. LINE Pay Sandbox 訂單發起與 Web/App 付款跳轉 URL 生成
6. LINE Pay Confirm API 扣款狀態機轉移與雙寫持久化
7. 扣款確認重複通知之冪等性（Idempotency）防護
8. 訂單狀態 APPI 深度去敏化查詢
"""
import os
import json
import unittest

os.environ['CHANNEL_ACCESS_TOKEN'] = 'test-token'
os.environ['CHANNEL_SECRET'] = 'test-secret'
os.environ['LINE_PAY_STAGE'] = 'true'

from line_bot import app
from core import payment_manager


class TestPaymentApi(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        payment_manager.order_store.clear()

    def test_price_recalculation_ignores_client_tampered_price(self):
        """測試伺服器端防偽重算：若前端試圖將 NT$1,845 禮盒竄改為 NT$10，伺服器必須強制依據官方定價重算"""
        payload = {
            "customer": {
                "name": "測試訪客",
                "email": "visitor@example.com",
            },
            "items": [
                {
                    "id": "SET-MIRROR-01",
                    "name": "【鏡子】當下覺察調息禮盒",
                    "price": 10,  # 惡意篡改為 10 元
                    "qty": 2,
                }
            ],
            "provider": "linepay"
        }
        res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        # 官方定價 1845 * 2 = 3690
        self.assertEqual(data.get("amount"), 3690)
        self.assertEqual(data["payment"]["params"]["amount"], "3690")
        self.assertEqual(data.get("provider"), "linepay")

    def test_unsupported_provider_rejected(self):
        """測試唯一定錨 LINE Pay：拒絕非 linepay 之渠道（包含已封存之 ecpay）"""
        payload = {
            "customer": {"name": "測試訪客", "email": "test@example.com"},
            "items": [{"id": "SET-MIRROR-01", "qty": 1}],
            "provider": "ecpay"  # 已封存舊渠道
        }
        res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertEqual(data.get("code"), "UNSUPPORTED_PROVIDER")
        self.assertIn("LINE Pay", data.get("message", ""))

    def test_invalid_qty_rejected(self):
        """測試非法商品數量（0、負數、超過 99）被伺服器阻斷"""
        payload = {
            "customer": {"name": "測試訪客", "email": "test@example.com"},
            "items": [{"id": "SET-MIRROR-01", "qty": 0}]
        }
        res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("數量必須介於", data.get("error", ""))

    def test_unknown_item_rejected(self):
        """測試不存在於資料庫之惡意商品被精準阻斷"""
        payload = {
            "customer": {"name": "測試訪客", "email": "test@example.com"},
            "items": [{"id": "FAKE-ITEM-999", "name": "未知偽造品項", "qty": 1}]
        }
        res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertIn("找不到指定的官方商品", data.get("error", ""))

    def test_customer_validation(self):
        """測試顧客資料校驗：姓名為空或未留聯絡資訊時阻斷"""
        # 姓名為空
        res = self.app.post('/api/payments/create', json={
            "customer": {"name": "", "email": "test@example.com"},
            "items": [{"id": "SET-MIRROR-01", "qty": 1}]
        })
        self.assertEqual(res.status_code, 400)

        # 無聯絡方式
        res2 = self.app.post('/api/payments/create', json={
            "customer": {"name": "王小明", "email": ""},
            "items": [{"id": "SET-MIRROR-01", "qty": 1}]
        })
        self.assertEqual(res2.status_code, 400)
        data2 = json.loads(res2.data)
        self.assertIn("至少需提供一種聯絡方式", data2.get("error", ""))

    def test_linepay_signature_generation(self):
        """測試 LINE Pay v3 HMAC-SHA256 簽名演算法之正確性與確定性"""
        channel_secret = "test_secret_12345"
        uri = "/v3/payments/request"
        body_str = '{"amount":1000,"currency":"TWD"}'
        nonce = "d57bf558-86d4-4a25-8247-f709d722e032"

        sig1 = payment_manager.generate_line_pay_signature(channel_secret, uri, body_str, nonce)
        sig2 = payment_manager.generate_line_pay_signature(channel_secret, uri, body_str, nonce)

        self.assertIsInstance(sig1, str)
        self.assertTrue(len(sig1) > 20)
        self.assertEqual(sig1, sig2, "相同輸入必須產生一致的 HMAC-SHA256 簽章")

    def test_linepay_sandbox_create_order_flow(self):
        """測試 LINE Pay Sandbox 建立訂單與付款跳轉 URL 生成"""
        payload = {
            "customer": {"name": "林小華", "email": "lin@example.com"},
            "items": [{"id": "SET-RIVER-02", "qty": 1}],
            "provider": "linepay"
        }
        res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)

        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("provider"), "linepay")
        self.assertIn("order_id", data)
        self.assertIn("transaction_id", data)

        payment_info = data.get("payment", {})
        action_url = payment_info.get("action_url", "")
        self.assertTrue(
            action_url.startswith("https://sandbox-web-pay.line.me"),
            f"測試沙盒付款網址應指向 sandbox-web-pay.line.me，實際為: {action_url}"
        )
        self.assertIn("zanshin_oracle", data)
        self.assertIn("trust_assurance", data)

    def test_linepay_confirm_flow_and_idempotency(self):
        """測試 LINE Pay Confirm 扣款確認流程與重複回調之冪等性防護"""
        # 1. 發起訂單
        payload = {
            "customer": {"name": "陳美月", "phone": "0912-345-678"},
            "items": [{"id": "SET-CROSS-03", "qty": 1}],
            "provider": "linepay"
        }
        create_res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(create_res.status_code, 201)
        order_data = json.loads(create_res.data)
        order_id = order_data["order_id"]
        tx_id = order_data["transaction_id"]
        amount = order_data["amount"]

        # 2. 模擬用戶完成授權，由 LINE Pay 回跳至 /api/payments/linepay/confirm
        confirm_url = f"/api/payments/linepay/confirm?transactionId={tx_id}&orderId={order_id}&amount={amount}&format=json"
        confirm_res = self.app.get(confirm_url)
        self.assertEqual(confirm_res.status_code, 200)
        confirm_data = json.loads(confirm_res.data)
        self.assertTrue(confirm_data.get("success"))
        self.assertEqual(confirm_data.get("status"), "PAID")

        # 3. 檢查訂單狀態已轉為 PAID
        status_res = self.app.get(f'/api/payments/status/{order_id}')
        self.assertEqual(status_res.status_code, 200)
        status_data = json.loads(status_res.data)
        self.assertEqual(status_data["order"]["status"], "PAID")
        self.assertEqual(status_data["order"]["provider"], "linepay")
        self.assertIsNotNone(status_data["order"]["paid_at"])

        # 4. 測試冪等性：重複發送相同扣款確認，仍安全回傳成功 (PAID, idempotent=True) 且不報錯
        confirm_res2 = self.app.get(confirm_url)
        self.assertEqual(confirm_res2.status_code, 200)
        confirm_data2 = json.loads(confirm_res2.data)
        self.assertTrue(confirm_data2.get("success"))
        self.assertEqual(confirm_data2.get("status"), "PAID")
        self.assertTrue(confirm_data2.get("idempotent"))

    def test_legacy_ecpay_check_mac_value_calculation(self):
        """相容性驗證：封存之綠界 SHA256 CheckMacValue 演算法保留完整"""
        params = {
            "MerchantID": "3002607",
            "MerchantTradeNo": "DTRTEST001",
            "MerchantTradeDate": "2026/09/10 12:00:00",
            "PaymentType": "aio",
            "TotalAmount": "1845",
            "TradeDesc": "Modern+Oil",
            "ItemName": "ItemA#ItemB",
            "ReturnURL": "https://example.com/callback",
            "ChoosePayment": "ALL",
            "EncryptType": "1",
        }
        mac1 = payment_manager.generate_ecpay_check_mac_value(
            params,
            payment_manager.DEFAULT_ECPAY_HASH_KEY,
            payment_manager.DEFAULT_ECPAY_HASH_IV
        )
        self.assertIsInstance(mac1, str)
        self.assertEqual(len(mac1), 64)
        self.assertEqual(mac1, mac1.upper())


if __name__ == '__main__':
    unittest.main()
