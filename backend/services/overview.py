from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List

from backend.collectors.gpu import get_gpu_processes, get_gpu_summary
from backend.collectors.node import get_node_runtime
from backend.collectors.slurm import get_jobs, get_nodes


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


def _collect_one_node(node: Dict, job_map_by_node: Dict[str, List[Dict]]) -> Dict:
    node_name = node["name"]
    node_state = node["state"]
    is_reachable = "down" not in node_state.lower()

    gpu_summary = []
    gpu_processes = []
    runtime = {
        "cpu_usage_percent": None,
        "mem_total_mb": None,
        "mem_used_mb": None,
        "mem_free_mb": None,
    }

    if is_reachable:
        with ThreadPoolExecutor(max_workers=3) as executor:
            f_gpu_summary = executor.submit(get_gpu_summary, node_name)
            f_gpu_processes = executor.submit(get_gpu_processes, node_name)
            f_runtime = executor.submit(get_node_runtime, node_name)

            gpu_summary = f_gpu_summary.result()
            gpu_processes = f_gpu_processes.result()
            runtime = f_runtime.result()

    proc_map: Dict[str, List[Dict]] = {}
    for proc in gpu_processes:
        proc = dict(proc)
        proc["runtime_human"] = _format_duration(proc.get("runtime_sec", 0))
        proc_map.setdefault(proc["gpu_uuid"], []).append(proc)

    gpu_cards = []
    node_busy_gpu_count = 0
    user_gpu_count: Dict[str, int] = {}
    user_proc_count: Dict[str, int] = {}

    for gpu in gpu_summary:
        processes = proc_map.get(gpu["uuid"], [])

        is_occupied = (
            len(processes) > 0
            or gpu["memory_used_mb"] >= 500
        )

        has_activity = gpu["utilization_gpu"] >= 30

        if is_occupied:
            node_busy_gpu_count += 1

        seen_users_on_this_gpu = set()
        for proc in processes:
            user = proc.get("user") or "unknown"
            user_proc_count[user] = user_proc_count.get(user, 0) + 1
            if user not in seen_users_on_this_gpu:
                user_gpu_count[user] = user_gpu_count.get(user, 0) + 1
                seen_users_on_this_gpu.add(user)

        gpu_cards.append({
            "index": gpu["index"],
            "uuid": gpu["uuid"],
            "name": gpu["name"],
            "utilization_gpu": gpu["utilization_gpu"],
            "memory_used_mb": gpu["memory_used_mb"],
            "memory_total_mb": gpu["memory_total_mb"],
            "temperature_gpu": gpu["temperature_gpu"],
            "is_busy": is_occupied,
            "is_occupied": is_occupied,
            "has_activity": has_activity,
            "process_count": len(processes),
            "processes": processes,
        })

    return {
        "name": node_name,
        "state": node_state,
        "gres": node["gres"],
        "reachable": is_reachable,
        "runtime": runtime,
        "gpus": gpu_cards,
        "slurm_jobs": job_map_by_node.get(node_name, []),
        "busy_gpu_count": node_busy_gpu_count,
        "idle_gpu_count": max(len(gpu_cards) - node_busy_gpu_count, 0),
        "_stats": {
            "total_gpus": len(gpu_cards),
            "busy_gpus": node_busy_gpu_count,
            "online_nodes": 1 if is_reachable else 0,
            "offline_nodes": 0 if is_reachable else 1,
            "user_gpu_count": user_gpu_count,
            "user_proc_count": user_proc_count,
        },
    }


def build_overview() -> Dict:
    jobs = get_jobs()
    nodes = get_nodes()

    job_map_by_node: Dict[str, List[Dict]] = {}
    for job in jobs:
        nodelist = job.get("nodelist", "")
        if nodelist and "," not in nodelist and "[" not in nodelist:
            job_map_by_node.setdefault(nodelist, []).append(job)

    node_views: List[Dict] = []
    total_gpus = 0
    busy_gpus = 0
    online_nodes = 0
    offline_nodes = 0
    user_gpu_count: Dict[str, int] = {}
    user_proc_count: Dict[str, int] = {}

    max_workers = min(max(len(nodes), 1), 16)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_collect_one_node, node, job_map_by_node)
            for node in nodes
        ]

        for future in as_completed(futures):
            node_view = future.result()
            stats = node_view.pop("_stats")

            total_gpus += stats["total_gpus"]
            busy_gpus += stats["busy_gpus"]
            online_nodes += stats["online_nodes"]
            offline_nodes += stats["offline_nodes"]

            for user, count in stats["user_gpu_count"].items():
                user_gpu_count[user] = user_gpu_count.get(user, 0) + count

            for user, count in stats["user_proc_count"].items():
                user_proc_count[user] = user_proc_count.get(user, 0) + count

            node_views.append(node_view)

    node_views.sort(
        key=lambda x: (
            0 if x["reachable"] else 1,
            -x["busy_gpu_count"],
            x["name"],
        )
    )

    users = []
    for user, gpu_count in user_gpu_count.items():
        users.append({
            "user": user,
            "gpu_count": gpu_count,
            "process_count": user_proc_count.get(user, 0),
        })
    users.sort(key=lambda x: (-x["gpu_count"], -x["process_count"], x["user"]))

    return {
        "summary": {
            "total_nodes": len(nodes),
            "online_nodes": online_nodes,
            "offline_nodes": offline_nodes,
            "total_gpus": total_gpus,
            "busy_gpus": busy_gpus,
            "idle_gpus": max(total_gpus - busy_gpus, 0),
            "running_jobs": len(jobs),
        },
        "users": users,
        "nodes": node_views,
    }