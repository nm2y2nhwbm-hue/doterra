# -*- coding: utf-8 -*-
"""
Agent 1 負責範圍：冷啟動預暖保溫模組 (core/keep_warm.py)
實裝日式「間（Ma）」之款待哲學，透過背景輕量守護 Worker 定期溫熱服務，
消除 Render 免費容器 15 分鐘休眠造成的 30~50 秒冷啟動延遲。
"""
import os
import time
import threading
import urllib.request
from datetime import datetime, timezone

_START_TIME = time.time()
_LAST_HEARTBEAT = datetime.now(timezone.utc).isoformat()
_WORKER_THREAD = None
_RUNNING = False
_LOCK = threading.Lock()


def _resolve_target_url():
    """解析保溫探測目標網址（優先採用 KEEP_WARM_TARGET_URL，缺省採用 Render 外部 Ingress 網址以有效維持喚醒）"""
    target = os.environ.get("KEEP_WARM_TARGET_URL")
    if target:
        return target
    base_url = os.environ.get("SERVER_BASE_URL", "https://doterra-73pv.onrender.com").rstrip("/")
    return f"{base_url}/health"


def get_warm_status():
    """取得當前伺服器保溫與存活狀態"""
    uptime = int(time.time() - _START_TIME)
    return {
        "status": "warm",
        "service": "modern-oil-oracle-warm-keeper",
        "uptime_seconds": uptime,
        "last_heartbeat": _LAST_HEARTBEAT,
        "keep_warm_active": _RUNNING,
        "target_url": _resolve_target_url(),
    }


def _ping_target(url):
    global _LAST_HEARTBEAT
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ModernOil-WarmKeeper/1.0 (Omotenashi-Ping)"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                with _LOCK:
                    _LAST_HEARTBEAT = datetime.now(timezone.utc).isoformat()
    except Exception:
        # 心跳失敗不中斷服務，僅記錄時間
        with _LOCK:
            _LAST_HEARTBEAT = datetime.now(timezone.utc).isoformat()


def _keep_warm_loop(interval_seconds=540):
    global _RUNNING
    # 預設每 9 分鐘探測一次（Render 免費方案於 15 分鐘無流量時休眠）
    while _RUNNING:
        time.sleep(interval_seconds)
        if not _RUNNING:
            break
        target_url = _resolve_target_url()
        _ping_target(target_url)


def start_keep_warm(interval_seconds=540):
    """啟動背景保溫守護 Daemon（在測試環境或顯式禁用時安全跳過）"""
    global _WORKER_THREAD, _RUNNING
    if os.environ.get("DISABLE_KEEP_WARM", "false").lower() in ("true", "1", "yes"):
        return False

    with _LOCK:
        if _RUNNING:
            return True
        _RUNNING = True
        _WORKER_THREAD = threading.Thread(
            target=_keep_warm_loop,
            args=(interval_seconds,),
            daemon=True,
            name="ModernOil-KeepWarmWorker"
        )
        _WORKER_THREAD.start()
        return True


def stop_keep_warm():
    """停止背景保溫守護 Daemon"""
    global _RUNNING
    with _LOCK:
        _RUNNING = False
