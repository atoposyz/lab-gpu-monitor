#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"

BACKEND_PID_FILE="$LOG_DIR/backend_prod.pid"

if [ ! -f "$BACKEND_PID_FILE" ]; then
  echo "[stop_prod] pid file not found: $BACKEND_PID_FILE"
  exit 0
fi

PID="$(cat "$BACKEND_PID_FILE" || true)"

if [ -z "${PID:-}" ]; then
  echo "[stop_prod] pid file is empty."
  rm -f "$BACKEND_PID_FILE"
  exit 0
fi

if ps -p "$PID" > /dev/null 2>&1; then
  echo "[stop_prod] Stopping backend production server (PID $PID) ..."
  kill "$PID" || true
  sleep 1

  if ps -p "$PID" > /dev/null 2>&1; then
    echo "[stop_prod] Process still alive, forcing kill ..."
    kill -9 "$PID" || true
  fi
else
  echo "[stop_prod] Process not running (PID $PID)"
fi

rm -f "$BACKEND_PID_FILE"
echo "[stop_prod] Done."