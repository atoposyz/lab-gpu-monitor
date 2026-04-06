from typing import Dict

from backend.collectors.ssh import safe_run_ssh


def get_node_runtime(node: str) -> Dict:
    cpu_idle = safe_run_ssh(
        node,
        "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/'"
    )
    mem_info = safe_run_ssh(
        node,
        "free -m | awk 'NR==2{print $2\" \"$3\" \"$4}'"
    )

    cpu_usage = None
    if cpu_idle:
        try:
            cpu_usage = round(100 - float(cpu_idle), 1)
        except ValueError:
            cpu_usage = None

    mem_total_mb = None
    mem_used_mb = None
    mem_free_mb = None
    if mem_info:
        parts = mem_info.split()
        if len(parts) == 3:
            try:
                mem_total_mb = int(parts[0])
                mem_used_mb = int(parts[1])
                mem_free_mb = int(parts[2])
            except ValueError:
                pass

    return {
        "cpu_usage_percent": cpu_usage,
        "mem_total_mb": mem_total_mb,
        "mem_used_mb": mem_used_mb,
        "mem_free_mb": mem_free_mb,
    }