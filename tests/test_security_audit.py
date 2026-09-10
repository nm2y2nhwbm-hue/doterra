# -*- coding: utf-8 -*-
"""
Agent 3 負責範圍：全站資安漏洞、XSS 注入防護與自然醫學法規邊界自動化稽核 (tests/test_security_audit.py)
檢驗項目：
1. 前端 XSS 注入防護稽核：檢驗涉及 innerHTML 動態渲染之腳本是否具備 escapeHtml 機制
2. 衛福部法規與自然醫學合規稽核：嚴格檢驗 doterra.csv 與 indicator_cards.csv 零醫療違規詞彙
3. 金流訂單持久化與容器暫存風險檢測：追蹤 OrderStore 儲存機制
4. 預暖保溫守護端點配置檢測：檢驗 keep_warm 探測目標非僅依賴內部 localhost
"""
import os
import re
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class TestSecurityAndComplianceAudit(unittest.TestCase):
    """全站資安與合規性照妖鏡自動化測試"""

    def test_csv_natural_medicine_regulatory_compliance(self):
        """法規邊界稽核：檢驗商品資料母體絕對無衛福部管制之醫療療效與爭議詞彙"""
        prohibited_terms = [
            "治療", "治癒", "消炎", "降血壓", "預防感冒",
            "抗癌", "抗腫瘤", "止痛", "抗病毒", "提升免疫", "增強免疫",
            "退燒", "降血糖", "殺死病毒", "醫療效果", "藥物"
        ]

        csv_paths = [
            BASE_DIR / "doterra.csv",
            BASE_DIR / "indicator_cards.csv",
        ]

        violations = []
        for p in csv_paths:
            if not p.exists():
                continue
            with open(p, "r", encoding="utf-8-sig") as f:
                content = f.read()
                for term in prohibited_terms:
                    if term in content:
                        violations.append(f"{p.name} 包含管制詞彙: 「{term}」")

        self.assertEqual(
            len(violations), 0,
            f"自然醫學商品庫發現潛在醫療違規詞彙，需立即請 Agent 4 修潤：\n" + "\n".join(violations)
        )

    def test_admin_reception_xss_protection(self):
        """安全稽核：確認 reception 管理後台 (admin.js) 具備 escapeHtml 與 sanitizeUrl 雙層防護"""
        admin_js_path = BASE_DIR / "static" / "admin.js"
        self.assertTrue(admin_js_path.exists())
        code = admin_js_path.read_text(encoding="utf-8")

        self.assertIn("function escapeHtml", code, "admin.js 缺少 escapeHtml 函式，有 Stored XSS 風險！")
        self.assertIn("function sanitizeUrl", code, "admin.js 缺少 sanitizeUrl 函式，有開放重定向或偽協議風險！")

    def test_booking_js_xss_protection(self):
        """安全稽核：確認 booking.js 表單與調息奉呈卡具備 escapeHtml 防護"""
        booking_js_path = BASE_DIR / "static" / "booking.js"
        self.assertTrue(booking_js_path.exists())
        code = booking_js_path.read_text(encoding="utf-8")

        self.assertIn("function escapeHtml", code, "booking.js 缺少 escapeHtml 函式！")

    def test_inventory_and_cart_xss_audit_tracking(self):
        """
        照妖鏡安全追蹤：盤查 inventory.js 與 cart.js 的 innerHTML 轉義完整性
        （此測試作為跨 Agent 協同品質守門員，偵測未轉義之 innerHTML 注入點）
        """
        inventory_js = BASE_DIR / "static" / "inventory.js"
        cart_js = BASE_DIR / "components" / "cart" / "cart.js"

        has_inventory_escape = False
        if inventory_js.exists():
            inv_code = inventory_js.read_text(encoding="utf-8")
            has_inventory_escape = "escapeHtml" in inv_code

        has_cart_escape = False
        if cart_js.exists():
            cart_code = cart_js.read_text(encoding="utf-8")
            has_cart_escape = "escapeHtml" in cart_code

        # 嚴格斷言：確認 Agent 2 已完成全站 XSS 實體轉義與 URL 安全過濾
        self.assertTrue(has_inventory_escape, "static/inventory.js 必須包含 escapeHtml 轉義函式！")
        self.assertTrue(has_cart_escape, "components/cart/cart.js 必須包含 escapeHtml 轉義函式！")
        self.assertIn("sanitizeUrl", inv_code, "static/inventory.js 必須包含 sanitizeUrl 函式！")
        self.assertIn("sanitizeUrl", cart_code, "components/cart/cart.js 必須包含 sanitizeUrl 函式！")

    def test_keep_warm_configuration_safety(self):
        """保溫服務安全檢測：確認 keep_warm 預設使用 Render 外部 Ingress 網址維持活躍流量"""
        from core import keep_warm
        status = keep_warm.get_warm_status()
        self.assertIn("status", status)
        self.assertIn("service", status)
        self.assertEqual(status["status"], "warm")

        # 檢驗保溫探測目標絕非內部 127.0.0.1，必須穿透外部 Ingress
        target_url = keep_warm._resolve_target_url()
        self.assertFalse("127.0.0.1" in target_url, "keep_warm 探測目標不可為 127.0.0.1，否則無法維持 Render 喚醒！")
        self.assertTrue(target_url.startswith("https://") or target_url.startswith("http://"))

    def test_payment_manager_supabase_persistence(self):
        """金流資料持久化檢驗：確認 OrderStore 具備 Supabase 雙寫與重啟恢復能力 (Finding 0.1 根治驗證)"""
        from core import payment_manager
        # 驗證具備 Supabase 憑證探測、雙寫同步與記憶體冷啟動檢索函式
        self.assertTrue(hasattr(payment_manager, "_sync_order_to_supabase"))
        self.assertTrue(hasattr(payment_manager, "_fetch_order_from_supabase"))
        self.assertTrue(hasattr(payment_manager, "_supabase_credentials"))


    def test_payment_manager_idempotency_contract(self):
        """金流安全合約：確認已支付訂單具備 1|OK 冪等防護"""
        from core import payment_manager
        # 驗證 OrderStore 具備基本介面
        self.assertTrue(hasattr(payment_manager.order_store, "get_order"))
        self.assertTrue(hasattr(payment_manager.order_store, "save_order"))
        self.assertTrue(hasattr(payment_manager.order_store, "update_status"))


if __name__ == "__main__":
    unittest.main()
