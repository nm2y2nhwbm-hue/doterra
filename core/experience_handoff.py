"""Secure browser-to-LINE draw handoff service.

The browser never receives a draw code. It receives a short-lived opaque token;
Render stores only the token hash in Supabase. LINE identity is accepted only
after the raw LIFF ID token has been verified by the LINE Platform.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import time
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache

from core import database_manager


LINE_VERIFY_URL = "https://api.line.me/oauth2/v2.1/verify"
HANDOFF_TTL_SECONDS = 600
HTTP_TIMEOUT_SECONDS = 8
EXPECTED_RESULT_COUNTS = {
    1: 1,
    2: 2,
    3: 3,
    4: 3,
    5: 3,
    6: 3,
    7: 3,
    8: 3,
    9: 3,
    10: 2,
    11: 4,
    12: 4,
}
TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{40,80}$")
CODE_PATTERN = re.compile(r"^INSIGHT-[A-Z0-9]+$", re.IGNORECASE)


class HandoffError(Exception):
    def __init__(self, public_message: str, status_code: int = 400):
        super().__init__(public_message)
        self.public_message = public_message
        self.status_code = status_code


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def get_readiness():
    """Report whether the handoff API has every required server setting.

    This deliberately returns setting names only, never secret values, so the
    production endpoint can be used for a read-only deployment smoke test.
    """
    missing = []
    if not _env("SUPABASE_URL"):
        missing.append("SUPABASE_URL")
    if not (_env("SUPABASE_SECRET_KEY") or _env("SUPABASE_SERVICE_ROLE_KEY")):
        missing.append("SUPABASE_SECRET_KEY_OR_SERVICE_ROLE_KEY")
    if not _env("LINE_LOGIN_CHANNEL_ID"):
        missing.append("LINE_LOGIN_CHANNEL_ID")
    if not (_env("HANDOFF_RATE_LIMIT_SECRET") or _env("CHANNEL_SECRET")):
        missing.append("HANDOFF_RATE_LIMIT_SECRET_OR_CHANNEL_SECRET")

    if missing:
        return {"status": "not_configured", "missing": missing}, 503
    return {"status": "ready"}, 200


def _supabase_config():
    url = _env("SUPABASE_URL").rstrip("/")
    secret_key = _env("SUPABASE_SECRET_KEY") or _env("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not secret_key:
        raise HandoffError("抽牌保存服務尚未完成設定", 503)
    return url, secret_key


def _supabase_headers(secret_key: str):
    headers = {
        "apikey": secret_key,
        "Content-Type": "application/json",
        "User-Agent": "doterra-render/1.0",
    }
    # New sb_secret_* keys are not JWTs and must not be sent as Bearer tokens.
    # Legacy service_role JWTs still need Authorization for PostgREST role auth.
    if not secret_key.startswith("sb_secret_"):
        headers["Authorization"] = f"Bearer {secret_key}"
    return headers


def _line_channel_id() -> str:
    channel_id = _env("LINE_LOGIN_CHANNEL_ID")
    if not channel_id:
        raise HandoffError("LINE 驗證服務尚未完成設定", 503)
    return channel_id


def build_request_fingerprint(remote_addr: str, user_agent: str) -> str:
    key = _env("HANDOFF_RATE_LIMIT_SECRET") or _env("CHANNEL_SECRET")
    if not key:
        raise HandoffError("抽牌保護服務尚未完成設定", 503)
    source = f"{remote_addr or 'unknown'}|{(user_agent or '')[:300]}".encode("utf-8")
    return hmac.new(key.encode("utf-8"), source, hashlib.sha256).hexdigest()


def _clean_text(value, max_length: int) -> str:
    return str(value or "").strip()[:max_length]


@lru_cache(maxsize=1)
def _card_catalog():
    cards = database_manager.fetch_oils_data() + database_manager.fetch_indicator_cards()
    return {card["name"]: card for card in cards if card.get("name")}


def _validated_draw(payload: dict):
    if not isinstance(payload, dict):
        raise HandoffError("抽牌資料格式不正確", 400)
    try:
        mode = int(payload.get("mode"))
    except (TypeError, ValueError):
        raise HandoffError("抽牌模式不正確", 400)
    if mode < 1 or mode > 12:
        raise HandoffError("抽牌模式不正確", 400)

    raw_results = payload.get("results")
    expected_count = EXPECTED_RESULT_COUNTS[mode]
    if not isinstance(raw_results, list) or len(raw_results) != expected_count:
        raise HandoffError("抽牌結果不完整", 400)

    results = []
    catalog = _card_catalog()
    for raw in raw_results:
        if not isinstance(raw, dict):
            raise HandoffError("抽牌結果格式不正確", 400)
        card_name = _clean_text(raw.get("card_name"), 100)
        canonical_card = catalog.get(card_name)
        if not canonical_card:
            raise HandoffError("抽牌結果包含未知牌卡", 400)
        label = _clean_text(raw.get("label"), 160)
        if not label or '<' in label or '>' in label:
            raise HandoffError("抽牌位置標籤不正確", 400)
        results.append({
            "label": label,
            "card_name": card_name,
            "card_name_en": _clean_text(canonical_card.get("name_en"), 120),
            "image_url": _clean_text(canonical_card.get("image_url"), 500),
        })
    return mode, results


def _supabase_rpc(function_name: str, payload: dict):
    url, secret_key = _supabase_config()
    request_body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    api_request = urllib.request.Request(
        f"{url}/rest/v1/rpc/{function_name}",
        data=request_body,
        headers=_supabase_headers(secret_key),
        method="POST",
    )
    try:
        with urllib.request.urlopen(api_request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError:
        raise HandoffError("抽牌保存服務暫時無法使用", 502)
    except (urllib.error.URLError, TimeoutError):
        raise HandoffError("抽牌保存服務暫時無法連線", 503)

    try:
        data = json.loads(response_body)
    except (TypeError, ValueError):
        raise HandoffError("抽牌保存服務回應異常", 502)
    if not isinstance(data, dict):
        raise HandoffError("抽牌保存服務回應異常", 502)
    return data


def _verify_line_id_token(id_token: str):
    token = _clean_text(id_token, 4096)
    if not token:
        raise HandoffError("需要由 LINE 登入後才能查看體驗碼", 401)

    channel_id = _line_channel_id()
    request_body = urllib.parse.urlencode({
        "id_token": token,
        "client_id": channel_id,
    }).encode("ascii")
    verify_request = urllib.request.Request(
        LINE_VERIFY_URL,
        data=request_body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(verify_request, timeout=HTTP_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError:
        raise HandoffError("LINE 登入驗證失敗，請重新開啟抽卡頁", 401)
    except (urllib.error.URLError, TimeoutError):
        raise HandoffError("LINE 驗證服務暫時無法連線", 503)

    try:
        profile = json.loads(response_body)
    except (TypeError, ValueError):
        raise HandoffError("LINE 驗證服務回應異常", 502)

    try:
        expires_at = int(profile.get("exp") or 0) if isinstance(profile, dict) else 0
    except (TypeError, ValueError):
        expires_at = 0

    if (
        not isinstance(profile, dict)
        or profile.get("aud") != channel_id
        or not profile.get("sub")
        or expires_at <= int(time.time())
    ):
        raise HandoffError("LINE 登入驗證失敗，請重新開啟抽卡頁", 401)

    return {
        "user_id": _clean_text(profile.get("sub"), 128),
        "display_name": _clean_text(profile.get("name"), 100),
    }


def create_draw(payload: dict, request_fingerprint: str):
    mode, results = _validated_draw(payload)
    id_token = _clean_text(payload.get("id_token"), 4096)
    line_identity = _verify_line_id_token(id_token) if id_token else None

    handoff_token = None
    handoff_hash = None
    if line_identity is None:
        handoff_token = secrets.token_urlsafe(32)
        handoff_hash = hashlib.sha256(handoff_token.encode("utf-8")).hexdigest()

    rpc_result = _supabase_rpc("backend_create_draw", {
        "p_mode": mode,
        "p_results": results,
        "p_line_user_id": line_identity["user_id"] if line_identity else None,
        "p_line_display_name": line_identity["display_name"] if line_identity else None,
        "p_handoff_token_hash": handoff_hash,
        "p_handoff_ttl_seconds": HANDOFF_TTL_SECONDS,
        "p_request_fingerprint": request_fingerprint,
    })

    if rpc_result.get("rate_limited") is True:
        raise HandoffError("操作過於頻繁，請十分鐘後再試", 429)

    code = _clean_text(rpc_result.get("code"), 40)
    if not CODE_PATTERN.fullmatch(code):
        raise HandoffError("抽牌保存服務未建立有效體驗碼", 502)

    if line_identity:
        return {"persisted": True, "line_verified": True, "code": code}
    return {
        "persisted": True,
        "line_verified": False,
        "handoff_token": handoff_token,
        "expires_in": HANDOFF_TTL_SECONDS,
    }


def redeem_draw(payload: dict):
    if not isinstance(payload, dict):
        raise HandoffError("交接資料格式不正確", 400)
    handoff_token = _clean_text(payload.get("handoff_token"), 100)
    if not TOKEN_PATTERN.fullmatch(handoff_token):
        raise HandoffError("交接連結無效，請回到瀏覽器重新抽卡", 400)

    line_identity = _verify_line_id_token(payload.get("id_token"))
    token_hash = hashlib.sha256(handoff_token.encode("utf-8")).hexdigest()
    rpc_result = _supabase_rpc("backend_redeem_draw_handoff", {
        "p_handoff_token_hash": token_hash,
        "p_line_user_id": line_identity["user_id"],
        "p_line_display_name": line_identity["display_name"],
    })

    status = rpc_result.get("status")
    if status == "expired":
        raise HandoffError("交接連結已逾時，請回到瀏覽器重新抽卡", 410)
    if status in ("invalid", "used"):
        raise HandoffError("交接連結無效或已由其他 LINE 帳號使用", 410)
    if status != "ok":
        raise HandoffError("抽牌交接服務回應異常", 502)

    code = _clean_text(rpc_result.get("code"), 40)
    try:
        mode, results = _validated_draw({
            "mode": rpc_result.get("mode"),
            "results": rpc_result.get("results"),
        })
    except HandoffError:
        raise HandoffError("抽牌交接資料不完整", 502)
    if not CODE_PATTERN.fullmatch(code):
        raise HandoffError("抽牌交接資料不完整", 502)

    return {
        "persisted": True,
        "line_verified": True,
        "code": code,
        "mode": mode,
        "results": results,
    }
