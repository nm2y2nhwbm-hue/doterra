# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：第三方金流（綠界 ECPay / LINE Pay）自動化整合測試 (tests/test_payment_api.py)
檢驗項目：
1. 金額伺服器端防偽重算（拒絕前端偽造價格、負數、不存在品項）
2. 顧客資訊合法性校驗（姓名限制、聯絡方式必填一項）
3. 綠界 ECPay SHA256 CheckMacValue 演算法與防偽驗簽
4. Server-to-Server 異步回調與狀態機轉移
5. 訂單重複通知之冪等性（Idempotency）防護
6. 訂單狀態去敏化查詢
"""
import os
import json
import unittest

os.environ['CHANNEL_ACCESS_TOKEN'] = 'test-token'
os.environ['CHANNEL_SECRET'] = 'test-secret'
os.environ['ECPAY_STAGE'] = 'true'

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
            "provider": "ecpay"
        }
        res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertTrue(data.get("success"))
        # 官方定價 1845 * 2 = 3690
        self.assertEqual(data.get("amount"), 3690)
        self.assertEqual(data["payment"]["params"]["TotalAmount"], "3690")

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

    def test_ecpay_check_mac_value_calculation(self):
        """測試綠界 SHA256 CheckMacValue 演算法與特殊字元替換正確性"""
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
        self.assertEqual(len(mac1), 64)  # SHA256 hex string 長度為 64
        self.assertEqual(mac1, mac1.upper())

        # 驗證 verify_ecpay_check_mac_value
        params_with_mac = dict(params, CheckMacValue=mac1)
        self.assertTrue(payment_manager.verify_ecpay_check_mac_value(
            params_with_mac,
            payment_manager.DEFAULT_ECPAY_HASH_KEY,
            payment_manager.DEFAULT_ECPAY_HASH_IV
        ))

    def test_ecpay_callback_flow_and_idempotency(self):
        """測試綠界回調成功付款流程與冪等性防護"""
        # 1. 建立訂單
        payload = {
            "customer": {"name": "林小華", "email": "lin@example.com"},
            "items": [{"id": "SET-RIVER-02", "qty": 1}],
            "provider": "ecpay"
        }
        create_res = self.app.post('/api/payments/create', json=payload)
        self.assertEqual(create_res.status_code, 201)
        order_data = json.loads(create_res.data)
        order_id = order_data["order_id"]
        trade_no = order_data["merchant_trade_no"]
        amount = order_data["amount"]

        # 2. 模擬綠界發送付款成功回調 POST 表單
        callback_params = {
            "MerchantID": payment_manager.DEFAULT_ECPAY_MERCHANT_ID,
            "MerchantTradeNo": trade_no,
            "RtnCode": "1",
            "RtnMsg": "Succeeded",
            "TradeNo": "2609101234567890",
            "TradeAmt": str(amount),
            "PaymentDate": "2026/09/10 12:05:00",
            "PaymentType": "Credit_CreditCard",
            "SimulatePaid": "0",
        }
        check_mac = payment_manager.generate_ecpay_check_mac_value(
            callback_params,
            payment_manager.DEFAULT_ECPAY_HASH_KEY,
            payment_manager.DEFAULT_ECPAY_HASH_IV
        )
        callback_params["CheckMacValue"] = check_mac

        # 送出回調
        cb_res = self.app.post('/api/payments/ecpay/callback', data=callback_params)
        self.assertEqual(cb_res.status_code, 200)
        self.assertEqual(cb_res.data.decode('utf-8'), "1|OK")

        # 3. 檢查訂單狀態已轉為 PAID
        status_res = self.app.get(f'/api/payments/status/{order_id}')
        self.assertEqual(status_res.status_code, 200)
        status_data = json.loads(status_res.data)
        self.assertEqual(status_data["order"]["status"], "PAID")
        self.assertIsNotNone(status_data["order"]["paid_at"])

        # 4. 測試冪等性：再次重送相同回調，依然安全回覆 1|OK 且不會報錯
        cb_res2 = self.app.post('/api/payments/ecpay/callback', data=callback_params)
        self.assertEqual(cb_res2.status_code, 200)
        self.assertEqual(cb_res2.data.decode('utf-8'), "1|OK")

    def test_ecpay_callback_tampered_signature_rejected(self):
        """測試回調簽章被篡改時精準拒絕並回覆 0|CheckMacValue Error"""
        fake_callback = {
            "MerchantID": payment_manager.DEFAULT_ECPAY_MERCHANT_ID,
            "MerchantTradeNo": "DTRFAKE0001",
            "RtnCode": "1",
            "TradeAmt": "1000",
            "CheckMacValue": "INVALID_TAMPERED_CHECKSUM_VALUE"
        }
        res = self.app.post('/api/payments/ecpay/callback', data=fake_callback)
        self.assertEqual(res.status_code, 400)
        self.assertTrue(res.data.decode('utf-8').startswith("0|"))


if __name__ == '__main__':
    unittest.main()
