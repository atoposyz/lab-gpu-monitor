#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"

BACKEND_PID_FILE="$LOG_DIR/backend_dev.pid"
FRONTEND_PID_FILE="$LOG_DIR/frontend_dev.pid"

stop_pid_file() {
  local pid_file="$1"
  local name="$2"

  if [ ! -f "$pid_file" ]; then
    echo "[stop_dev] $name pid file not found: $pid_file"
    return 0
  fi

  local pid
  pid="$(cat "$pid_file" || true)"

  if [ -z "${pid:-}" ]; then
    echo "[stop_dev] $name pid file is empty: $pid_file"
    rm -f "$pid_file"
    return 0
  fi

  if ps -p "$pid" > /dev/null 2>&1; then
    echo "[stop_dev] Stopping $name (PID $pid) ..."
    kill "$pid" || true
    sleep 1

    if ps -p "$pid" > /dev/null 2>&1; then
      echo "[stop_dev] $name still alive, forcing kill ..."
      kill -9 "$pid" || true
    fi
  else
    echo "[stop_dev] $name process not running (PID $pid)"
  fi

  rm -f "$pid_file"
}

stop_pid_file "$FRONTEND_PID_FILE" "frontend dev server"
stop_pid_file "$BACKEND_PID_FILE" "backend dev server"

echo "[stop_dev] Done."