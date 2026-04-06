from typing import Dict, List

from backend.collectors.ssh import safe_run_ssh


def get_gpu_summary(node: str) -> List[Dict]:
    query = (
        "nvidia-smi "
        "--query-gpu=index,uuid,name,utilization.gpu,memory.used,memory.total,temperature.gpu "
        "--format=csv,noheader,nounits"
    )
    out = safe_run_ssh(node, query)
    gpus = []

    if not out:
        return gpus

    for line in out.splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 7:
            continue
        try:
            gpus.append({
                "index": parts[0],
                "uuid": parts[1],
                "name": parts[2],
                "utilization_gpu": int(parts[3]),
                "memory_used_mb": int(parts[4]),
                "memory_total_mb": int(parts[5]),
                "temperature_gpu": int(parts[6]),
            })
        except ValueError:
            continue
    return gpus


def _get_pid_metadata_batch(node: str, pids: List[int]) -> Dict[int, Dict]:
    if not pids:
        return {}

    pid_str = ",".join(str(pid) for pid in sorted(set(pids)))

    # 一次性批量查询所有 PID 的 user / etimes / cmd
    # etimes = elapsed time in seconds
    query = f"ps -p {pid_str} -o pid=,user=,etimes=,cmd="
    out = safe_run_ssh(node, query)

    result: Dict[int, Dict] = {}

    if not out:
        return result

    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue

        # 只切前 3 段，剩下整段保留为 cmd，避免命令行中空格被打散
        parts = line.split(None, 3)
        if len(parts) < 3:
            continue

        try:
            pid = int(parts[0])
            user = parts[1]
            runtime_sec = int(parts[2])
            cmdline = parts[3].strip() if len(parts) >= 4 else ""
        except ValueError:
            continue

        result[pid] = {
            "user": user,
            "runtime_sec": runtime_sec,
            "cmdline": cmdline,
        }

    return result


def get_gpu_processes(node: str) -> List[Dict]:
    query = (
        "nvidia-smi "
        "--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory "
        "--format=csv,noheader,nounits"
    )
    out = safe_run_ssh(node, query)
    processes = []

    if not out:
        return processes

    raw_rows = []
    pids: List[int] = []

    for line in out.splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 4:
            continue

        gpu_uuid, pid_str, process_name, used_gpu_memory_str = parts

        try:
            pid = int(pid_str)
            used_gpu_memory_mb = int(used_gpu_memory_str)
        except ValueError:
            continue

        raw_rows.append({
            "gpu_uuid": gpu_uuid,
            "pid": pid,
            "process_name": process_name,
            "used_gpu_memory_mb": used_gpu_memory_mb,
        })
        pids.append(pid)

    pid_meta = _get_pid_metadata_batch(node, pids)

    for row in raw_rows:
        meta = pid_meta.get(row["pid"], {})

        cmdline = meta.get("cmdline") or row["process_name"]

        processes.append({
            "gpu_uuid": row["gpu_uuid"],
            "pid": row["pid"],
            "process_name": row["process_name"],
            "used_gpu_memory_mb": row["used_gpu_memory_mb"],
            "user": meta.get("user", ""),
            "cmdline": cmdline,
            "runtime_sec": meta.get("runtime_sec", 0),
        })

    return processes