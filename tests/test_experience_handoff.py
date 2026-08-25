import hashlib
import os
import unittest
from unittest.mock import patch

from core import experience_handoff as handoff


VALID_RESULTS = [{
    "label": "今日心靈小語",
    "card_name": "薰衣草",
    "card_name_en": "Lavender",
    "image_url": "https://example.com/lavender.jpg",
}]


class ExperienceHandoffTests(unittest.TestCase):
    def test_readiness_reports_missing_settings_without_values(self):
        with patch.dict(os.environ, {}, clear=True):
            payload, status = handoff.get_readiness()

        self.assertEqual(status, 503)
        self.assertEqual(payload["status"], "not_configured")
        self.assertEqual(payload["missing"], [
            "SUPABASE_URL",
            "SUPABASE_SECRET_KEY_OR_SERVICE_ROLE_KEY",
            "LINE_LOGIN_CHANNEL_ID",
            "HANDOFF_RATE_LIMIT_SECRET_OR_CHANNEL_SECRET",
        ])

    def test_readiness_accepts_supported_fallback_settings(self):
        environment = {
            "SUPABASE_URL": "https://example.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "legacy-service-role",
            "LINE_LOGIN_CHANNEL_ID": "1234567890",
            "CHANNEL_SECRET": "rate-limit-key",
        }
        with patch.dict(os.environ, environment, clear=True):
            payload, status = handoff.get_readiness()

        self.assertEqual(status, 200)
        self.assertEqual(payload, {"status": "ready"})

    def test_new_supabase_secret_key_is_not_sent_as_bearer(self):
        headers = handoff._supabase_headers("sb_secret_example")

        self.assertEqual(headers["apikey"], "sb_secret_example")
        self.assertNotIn("Authorization", headers)

    def test_legacy_service_role_key_is_sent_as_bearer(self):
        headers = handoff._supabase_headers("legacy-jwt")

        self.assertEqual(headers["apikey"], "legacy-jwt")
        self.assertEqual(headers["Authorization"], "Bearer legacy-jwt")

    @patch.object(handoff, "_supabase_rpc")
    @patch.object(handoff.secrets, "token_urlsafe", return_value="A" * 43)
    def test_browser_draw_returns_handoff_without_code(self, _token, rpc):
        rpc.return_value = {"rate_limited": False, "code": "INSIGHT-ABC234"}

        result = handoff.create_draw({"mode": 1, "results": VALID_RESULTS}, "b" * 64)

        self.assertTrue(result["persisted"])
        self.assertFalse(result["line_verified"])
        self.assertEqual(result["handoff_token"], "A" * 43)
        self.assertNotIn("code", result)
        sent = rpc.call_args.args[1]
        self.assertEqual(
            sent["p_handoff_token_hash"],
            hashlib.sha256(("A" * 43).encode("utf-8")).hexdigest(),
        )
        self.assertNotEqual(sent["p_results"][0]["image_url"], VALID_RESULTS[0]["image_url"])

    @patch.object(handoff, "_supabase_rpc")
    @patch.object(handoff, "_verify_line_id_token")
    def test_line_draw_returns_code_after_server_verification(self, verify, rpc):
        verify.return_value = {"user_id": "U123", "display_name": "測試"}
        rpc.return_value = {"rate_limited": False, "code": "INSIGHT-ABC234"}

        result = handoff.create_draw({
            "mode": 1,
            "results": VALID_RESULTS,
            "id_token": "signed-token",
        }, "c" * 64)

        self.assertTrue(result["line_verified"])
        self.assertEqual(result["code"], "INSIGHT-ABC234")
        self.assertIsNone(rpc.call_args.args[1]["p_handoff_token_hash"])

    @patch.object(handoff, "_supabase_rpc")
    @patch.object(handoff, "_verify_line_id_token")
    def test_redeem_returns_original_draw(self, verify, rpc):
        verify.return_value = {"user_id": "U123", "display_name": "測試"}
        rpc.return_value = {
            "status": "ok",
            "code": "INSIGHT-ABC234",
            "mode": 1,
            "results": VALID_RESULTS,
        }

        result = handoff.redeem_draw({
            "handoff_token": "D" * 43,
            "id_token": "signed-token",
        })

        self.assertEqual(result["code"], "INSIGHT-ABC234")
        self.assertEqual(result["results"][0]["card_name"], VALID_RESULTS[0]["card_name"])
        self.assertEqual(result["results"][0]["label"], VALID_RESULTS[0]["label"])
        self.assertNotEqual(result["results"][0]["image_url"], VALID_RESULTS[0]["image_url"])
        self.assertTrue(result["line_verified"])

    def test_rejects_invalid_draw_payload(self):
        with self.assertRaises(handoff.HandoffError):
            handoff.create_draw({"mode": 99, "results": []}, "e" * 64)

    def test_rejects_incomplete_draw_for_mode(self):
        with self.assertRaisesRegex(handoff.HandoffError, "不完整"):
            handoff.create_draw({"mode": 2, "results": VALID_RESULTS}, "1" * 64)

    def test_rejects_unknown_card(self):
        with self.assertRaisesRegex(handoff.HandoffError, "未知牌卡"):
            handoff.create_draw({
                "mode": 1,
                "results": [{
                    **VALID_RESULTS[0],
                    "card_name": "不存在的牌卡",
                }],
            }, "f" * 64)

    def test_rejects_html_in_position_label(self):
        with self.assertRaisesRegex(handoff.HandoffError, "位置標籤"):
            handoff.create_draw({
                "mode": 1,
                "results": [{
                    **VALID_RESULTS[0],
                    "label": "<img src=x onerror=alert(1)>",
                }],
            }, "0" * 64)


if __name__ == "__main__":
    unittest.main()
