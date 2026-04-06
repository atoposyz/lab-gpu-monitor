#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
mkdir -p "$LOG_DIR"

BACKEND_PID_FILE="$LOG_DIR/backend_dev.pid"
FRONTEND_PID_FILE="$LOG_DIR/frontend_dev.pid"

BACKEND_LOG="$LOG_DIR/backend_dev.log"
FRONTEND_LOG="$LOG_DIR/frontend_dev.log"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

echo "[run_dev] Project root: $PROJECT_ROOT"
echo "[run_dev] Logs dir: $LOG_DIR"

# 检查 backend 端口是否被占用
if ss -lnt | awk '{print $4}' | grep -q ":${BACKEND_PORT}\$"; then
  echo "[run_dev] ERROR: backend port ${BACKEND_PORT} is already in use."
  exit 1
fi

# 检查 frontend 端口是否被占用
if ss -lnt | awk '{print $4}' | grep -q ":${FRONTEND_PORT}\$"; then
  echo "[run_dev] ERROR: frontend port ${FRONTEND_PORT} is already in use."
  exit 1
fi

echo "[run_dev] Starting backend on ${BACKEND_HOST}:${BACKEND_PORT} ..."
(
  cd "$PROJECT_ROOT"
  APP_ENV=dev uv run uvicorn backend.main:app \
    --host "$BACKEND_HOST" \
    --port "$BACKEND_PORT" \
    --reload
) >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

echo "[run_dev] Backend PID: $BACKEND_PID"
echo "[run_dev] Backend log: $BACKEND_LOG"

# 确保前端依赖已安装
if [ ! -d "$PROJECT_ROOT/frontend/node_modules" ]; then
  echo "[run_dev] frontend/node_modules not found, running npm install ..."
  (
    cd "$PROJECT_ROOT/frontend"
    npm install
  )
fi

echo "[run_dev] Starting frontend on ${FRONTEND_HOST}:${FRONTEND_PORT} ..."
(
  cd "$PROJECT_ROOT/frontend"
  npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT"
) >"$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > "$FRONTEND_PID_FILE"

echo "[run_dev] Frontend PID: $FRONTEND_PID"
echo "[run_dev] Frontend log: $FRONTEND_LOG"

sleep 2

echo
echo "[run_dev] Development services started."
echo "[run_dev] Frontend: http://127.0.0.1:${FRONTEND_PORT}"
echo "[run_dev] Backend API: http://127.0.0.1:${BACKEND_PORT}/api/overview"
echo "[run_dev] Stop them with: ./stop_dev.sh"
echo
echo "[run_dev] Tail logs:"
echo "  tail -f $BACKEND_LOG"
echo "  tail -f $FRONTEND_LOG"