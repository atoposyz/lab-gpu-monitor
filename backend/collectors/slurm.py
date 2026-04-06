import subprocess
from typing import List, Dict


def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def get_jobs() -> List[Dict]:
    fmt = "%i|%u|%j|%T|%P|%M|%D|%R"
    out = run_cmd(["squeue", "-h", "-o", fmt])
    jobs = []

    if not out:
        return jobs

    for line in out.splitlines():
        parts = line.split("|", 7)
        if len(parts) != 8:
            continue
        job_id, user, name, state, partition, time_used, nodes, nodelist = parts
        jobs.append({
            "job_id": job_id,
            "user": user,
            "name": name,
            "state": state,
            "partition": partition,
            "time_used": time_used,
            "nodes": nodes,
            "nodelist": nodelist,
        })
    return jobs


def get_nodes() -> List[Dict]:
    fmt = "%N|%T|%G"
    out = run_cmd(["sinfo", "-N", "-h", "-o", fmt])
    nodes = []

    if not out:
        return nodes

    for line in out.splitlines():
        parts = line.split("|", 2)
        if len(parts) != 3:
            continue
        name, state, gres = parts
        nodes.append({
            "name": name,
            "state": state,
            "gres": gres,
        })
    return nodes