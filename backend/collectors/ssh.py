import os
import subprocess

CONTROL_PATH = os.path.expanduser("~/.ssh/cm-%r@%h:%p")

SSH_BASE_OPTS = [
    "ssh",
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=2",
    "-o", "ConnectionAttempts=1",
    "-o", "ServerAliveInterval=5",
    "-o", "ServerAliveCountMax=1",
    "-o", "ControlMaster=auto",
    "-o", "ControlPersist=600",
    "-o", f"ControlPath={CONTROL_PATH}",
]


def run_ssh(node: str, remote_cmd: str) -> str:
    result = subprocess.run(
        SSH_BASE_OPTS + [node, remote_cmd],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def safe_run_ssh(node: str, remote_cmd: str) -> str:
    try:
        return run_ssh(node, remote_cmd)
    except subprocess.CalledProcessError:
        return ""