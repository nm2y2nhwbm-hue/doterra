# -*- coding: utf-8 -*-
"""
Agent 1 負責範圍：後端 API 路由藍圖 (api/routes.py)
包含健康檢查、精油與指示卡資料查詢、抽卡紀錄、體驗碼交接等核心端點。
"""
from flask import Blueprint, request, jsonify, Response
from core import database_manager as db
from core import draw_logger
from core import experience_handoff
from core import payment_manager

api_bp = Blueprint('api', __name__)


def _no_store_json(payload, status=200):
    response = jsonify(payload)
    response.status_code = status
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    return response


def _handoff_error_response(error):
    return _no_store_json({
        "persisted": False,
        "error": error.public_message,
    }, error.status_code)


def _request_client_ip():
    # 支援 Cloudflare、反向代理與 Render 轉發標頭
    for header in ('CF-Connecting-IP', 'X-Real-IP', 'X-Forwarded-For'):
        forwarded = request.headers.get(header, '')
        if forwarded:
            client_ip = forwarded.split(',', 1)[0].strip()
            if client_ip:
                return client_ip[:64]
    return (request.remote_addr or '')[:64]


@api_bp.route("/health", methods=['GET'])
def health():
    """後端伺服器存活與健康檢查端點。"""
    try:
        oils_count = len(db.fetch_oils_data())
    except Exception:
        oils_count = 0
    return jsonify({
        "status": "ok",
        "service": "modern-oil-oracle-api",
        "version": "2.2.0",
        "catalog_items": oils_count,
    })


@api_bp.route("/api/oils", methods=['GET'])
def api_oils():
    """回傳 131 款精油自然醫學資料庫（含容量與建議零售價）。"""
    return jsonify(db.fetch_oils_data())


@api_bp.route("/api/indicators", methods=['GET'])
def api_indicators():
    """回傳 12 款指示卡資料庫。"""
    return jsonify(db.fetch_indicator_cards())


@api_bp.route("/api/log-draw", methods=['POST'])
def api_log_draw():
    """記錄抽卡事件（模式、抽中卡片與使用者資訊）。"""
    data = request.get_json(silent=True) or {}
    ok = draw_logger.log_draw(
        user_id=data.get('user_id', ''),
        display_name=data.get('display_name', ''),
        mode=data.get('mode', ''),
        card_names=data.get('cards', []),
    )
    return jsonify({"success": ok})


@api_bp.route("/api/draws/health", methods=['GET'])
def api_draws_health():
    """抽卡交接服務健康探測。"""
    payload, status = experience_handoff.get_readiness()
    return _no_store_json(payload, status)


@api_bp.route("/api/draws", methods=['POST'])
def api_create_draw():
    """建立抽卡紀錄並派發短效 Opaque Handoff Token。"""
    data = request.get_json(silent=True) or {}
    try:
        fingerprint = experience_handoff.build_request_fingerprint(
            _request_client_ip(),
            request.headers.get('User-Agent', ''),
        )
        result = experience_handoff.create_draw(data, fingerprint)
        return _no_store_json(result)
    except experience_handoff.HandoffError as error:
        return _handoff_error_response(error)


@api_bp.route("/api/draws/redeem", methods=['POST'])
def api_redeem_draw():
    """LINE 用戶兌換並解鎖體驗碼。"""
    data = request.get_json(silent=True) or {}
    try:
        result = experience_handoff.redeem_draw(data)
        return _no_store_json(result)
    except experience_handoff.HandoffError as error:
        return _handoff_error_response(error)


# =========================================================================
# 💳 第三方金流（綠界 ECPay / LINE Pay）API 路由
# =========================================================================

@api_bp.route("/api/payments/create", methods=['POST'])
def api_create_payment():
    """建立付款訂單（強制伺服器端重算金額並產出金流表單參數）"""
    data = request.get_json(silent=True) or {}
    try:
        client_ip = _request_client_ip()
        result = payment_manager.create_payment_order(data, client_ip=client_ip)
        return _no_store_json(result, 201)
    except payment_manager.PaymentValidationError as error:
        return _no_store_json({"success": False, "error": error.message}, error.status_code)
    except Exception as e:
        return _no_store_json({"success": False, "error": "伺服器內部錯誤"}, 500)


@api_bp.route("/api/payments/ecpay/callback", methods=['POST'])
def api_ecpay_callback():
    """綠界 ECPay 異步背景通知回調（Server-to-Server）"""
    form_data = request.form.to_dict()
    if not form_data:
        form_data = request.get_json(silent=True) or {}
    try:
        response_text = payment_manager.process_ecpay_callback(form_data)
        return Response(response_text, mimetype='text/plain')
    except (payment_manager.PaymentSignatureError, payment_manager.PaymentValidationError) as error:
        return f"0|{error.message}", 400
    except Exception as e:
        return "0|Internal Error", 500


@api_bp.route("/api/payments/status/<order_id>", methods=['GET'])
def api_payment_status(order_id):
    """查詢訂單付款狀態"""
    status_info = payment_manager.get_order_status(order_id)
    if not status_info:
        return _no_store_json({"success": False, "error": "查無此訂單"}, 404)
    return _no_store_json({"success": True, "order": status_info})
