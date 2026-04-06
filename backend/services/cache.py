import threading
import time
from collections import defaultdict, deque
from copy import deepcopy
from typing import Any, Deque, Dict

from backend.services.overview import build_overview

_REFRESH_INTERVAL = 10
_HISTORY_POINTS = 120

# 可调参数
_OCCUPIED_MEM_THRESHOLD_MB = 500
_IDLE_UTIL_THRESHOLD = 5
_IDLE_MEM_THRESHOLD_MB = 500
_IDLE_SUSPECT_SEC = 600  # 10分钟

_cache_lock = threading.Lock()
_gpu_history: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=_HISTORY_POINTS))
_user_history: Dict[str, Deque[Dict[str, Any]]] = defaultdict(lambda: deque(maxlen=_HISTORY_POINTS))

# 每张 GPU 的跨周期状态
_gpu_state: Dict[str, Dict[str, Any]] = defaultdict(dict)

_cache_data: Dict[str, Any] = {
    "summary": {
        "total_nodes": 0,
        "online_nodes": 0,
        "offline_nodes": 0,
        "total_gpus": 0,
        "busy_gpus": 0,
        "idle_gpus": 0,
        "running_jobs": 0,
    },
    "users": [],
    "nodes": [],
    "history": {
        "gpus": {},
        "users": {},
        "max_points": _HISTORY_POINTS,
    },
    "_meta": {
        "status": "init",
        "last_update_ts": None,
        "last_update_iso": None,
        "refresh_interval_sec": _REFRESH_INTERVAL,
        "last_duration_sec": None,
        "last_error": None,
    },
}
_worker_started = False


def _now_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _format_duration(sec: int) -> str:
    if not sec or sec <= 0:
        return "0s"
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        m = sec // 60
        s = sec % 60
        return f"{m}m{s}s"
    if sec < 86400:
        h = sec // 3600
        m = (sec % 3600) // 60
        return f"{h}h{m}m"
    d = sec // 86400
    h = (sec % 86400) // 3600
    return f"{d}d{h}h"


def _gpu_key(node_name: str, gpu: Dict[str, Any]) -> str:
    return f'{node_name}::{gpu["index"]}'


def _attach_history(data: Dict[str, Any]) -> Dict[str, Any]:
    gpu_hist = {k: list(v) for k, v in _gpu_history.items()}
    user_hist = {k: list(v) for k, v in _user_history.items()}
    data["history"] = {
        "gpus": gpu_hist,
        "users": user_hist,
        "max_points": _HISTORY_POINTS,
    }
    return data


def _update_histories(data: Dict[str, Any]) -> None:
    ts = time.time()

    current_gpu_keys = set()
    for node in data.get("nodes", []):
        for gpu in node.get("gpus", []):
            key = _gpu_key(node["name"], gpu)
            current_gpu_keys.add(key)
            _gpu_history[key].append({
                "ts": ts,
                "util": gpu["utilization_gpu"],
                "mem": gpu["memory_used_mb"],
                "proc_count": len(gpu.get("processes", [])),
            })

    for key in list(_gpu_history.keys()):
        if key not in current_gpu_keys:
            _gpu_history[key].append({
                "ts": ts,
                "util": 0,
                "mem": 0,
                "proc_count": 0,
            })

    current_users = {
        item["user"]: {
            "gpu_count": item["gpu_count"],
            "process_count": item["process_count"],
        }
        for item in data.get("users", [])
    }

    all_users = set(_user_history.keys()) | set(current_users.keys())
    for user in all_users:
        info = current_users.get(user, {"gpu_count": 0, "process_count": 0})
        _user_history[user].append({
            "ts": ts,
            "gpu_count": info["gpu_count"],
            "process_count": info["process_count"],
        })


def _update_gpu_states(data: Dict[str, Any]) -> None:
    now = time.time()
    current_gpu_keys = set()

    for node in data.get("nodes", []):
        node_name = node["name"]

        for gpu in node.get("gpus", []):
            key = _gpu_key(node_name, gpu)
            current_gpu_keys.add(key)

            state = _gpu_state[key]

            proc_count = len(gpu.get("processes", []))
            util = gpu.get("utilization_gpu", 0) or 0
            mem = gpu.get("memory_used_mb", 0) or 0

            is_occupied = (
                proc_count > 0
                or mem >= _OCCUPIED_MEM_THRESHOLD_MB
            )

            is_idle_like = (
                proc_count > 0
                and util < _IDLE_UTIL_THRESHOLD
                and mem < _IDLE_MEM_THRESHOLD_MB
            )

            # 占用状态跟踪
            if is_occupied:
                if not state.get("is_occupied", False):
                    state["occupied_since_ts"] = now
                state["last_seen_occupied_ts"] = now
            else:
                state["occupied_since_ts"] = None
                state["last_seen_occupied_ts"] = None

            # 疑似 idle 跟踪
            if is_idle_like:
                if not state.get("is_idle_like", False):
                    state["idle_since_ts"] = now
                state["last_seen_idle_ts"] = now
            else:
                state["idle_since_ts"] = None
                state["last_seen_idle_ts"] = None

            state["is_occupied"] = is_occupied
            state["is_idle_like"] = is_idle_like
            state["last_seen_ts"] = now

    # 对本轮没出现的 GPU，清空活动状态
    for key in list(_gpu_state.keys()):
        if key not in current_gpu_keys:
            state = _gpu_state[key]
            state["is_occupied"] = False
            state["is_idle_like"] = False
            state["occupied_since_ts"] = None
            state["idle_since_ts"] = None
            state["last_seen_ts"] = now


def _attach_gpu_states(data: Dict[str, Any]) -> Dict[str, Any]:
    now = time.time()

    for node in data.get("nodes", []):
        for gpu in node.get("gpus", []):
            key = _gpu_key(node["name"], gpu)
            state = _gpu_state.get(key, {})

            occupied_since_ts = state.get("occupied_since_ts")
            idle_since_ts = state.get("idle_since_ts")

            occupied_duration_sec = (
                int(now - occupied_since_ts) if occupied_since_ts else 0
            )
            idle_duration_sec = (
                int(now - idle_since_ts) if idle_since_ts else 0
            )

            gpu["occupied_since_ts"] = occupied_since_ts
            gpu["occupied_duration_sec"] = occupied_duration_sec
            gpu["occupied_duration_human"] = _format_duration(occupied_duration_sec)

            gpu["idle_since_ts"] = idle_since_ts
            gpu["idle_duration_sec"] = idle_duration_sec
            gpu["idle_duration_human"] = _format_duration(idle_duration_sec)

            gpu["idle_suspected"] = idle_duration_sec >= _IDLE_SUSPECT_SEC

    return data


def _set_cache(data: Dict[str, Any]) -> None:
    with _cache_lock:
        _cache_data.clear()
        _cache_data.update(data)


def get_cached_overview() -> Dict[str, Any]:
    with _cache_lock:
        return deepcopy(_cache_data)


def refresh_overview_once() -> None:
    start = time.time()
    old_data = get_cached_overview()

    try:
        data = build_overview()

        _update_histories(data)
        _update_gpu_states(data)
        data = _attach_gpu_states(data)

        duration = round(time.time() - start, 3)

        data = _attach_history(data)
        data["_meta"] = {
            "status": "ok",
            "last_update_ts": time.time(),
            "last_update_iso": _now_iso(),
            "refresh_interval_sec": _REFRESH_INTERVAL,
            "last_duration_sec": duration,
            "last_error": None,
        }
        _set_cache(data)
    except Exception as e:
        duration = round(time.time() - start, 3)
        old_data["_meta"] = {
            "status": "error",
            "last_update_ts": old_data.get("_meta", {}).get("last_update_ts"),
            "last_update_iso": old_data.get("_meta", {}).get("last_update_iso"),
            "refresh_interval_sec": _REFRESH_INTERVAL,
            "last_duration_sec": duration,
            "last_error": str(e),
        }
        _set_cache(old_data)


def _worker_loop() -> None:
    while True:
        refresh_overview_once()
        time.sleep(_REFRESH_INTERVAL)


def start_background_refresh() -> None:
    global _worker_started
    if _worker_started:
        return

    _worker_started = True
    t = threading.Thread(target=_worker_loop, daemon=True)
    t.start()