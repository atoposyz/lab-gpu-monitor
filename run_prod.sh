#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

BACKEND_PID_FILE="$LOG_DIR/backend_prod.pid"
BACKEND_LOG="$LOG_DIR/backend_prod.log"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

echo "[run_prod] Project root: $PROJECT_ROOT"
echo "[run_prod] Logs dir: $LOG_DIR"

if ss -lnt | awk '{print $4}' | grep -q ":${BACKEND_PORT}\$"; then
  echo "[run_prod] ERROR: backend port ${BACKEND_PORT} is already in use."
  exit 1
fi

if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
  echo "[run_prod] frontend/node_modules not found, running npm install ..."
  (
    cd "$PROJECT_ROOT/frontend"
    npm install
  )
fi

echo "[run_prod] Building frontend ..."
(
  cd "$PROJECT_ROOT/frontend"
  npm run build
)

if [ ! -f "$PROJECT_ROOT/frontend/dist/index.html" ]; then
  echo "[run_prod] ERROR: build failed, frontend/dist/index.html not found."
  exit 1
fi

echo "[run_prod] Starting backend in production mode on ${BACKEND_HOST}:${BACKEND_PORT} ..."
(
  cd "$PROJECT_ROOT"
  APP_ENV=prod uv run uvicorn backend.main:app \
    --host "$BACKEND_HOST" \
    --port "$BACKEND_PORT"
) >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

sleep 2

echo "[run_prod] Backend PID: $BACKEND_PID"
echo "[run_prod] Backend log: $BACKEND_LOG"
echo
echo "[run_prod] Production service started."
echo "[run_prod] URL: http://127.0.0.1:${BACKEND_PORT}"
echo "[run_prod] Stop it with: ./stop_prod.sh"
echo
echo "[run_prod] Tail log:"
echo "  tail -f $BACKEND_LOG"