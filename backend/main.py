import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect

from backend.services.cache import get_cached_overview, start_background_refresh


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
DIST_ASSETS_DIR = DIST_DIR / "assets"

# 可选值：
# APP_ENV=dev   -> 开发模式，不托管前端 dist
# APP_ENV=prod  -> 生产模式，托管 frontend/dist
APP_ENV = os.getenv("APP_ENV", "dev").lower()
IS_PROD = APP_ENV == "prod"


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_background_refresh()
    yield


app = FastAPI(title="Lab GPU Monitor", lifespan=lifespan)


# ----------------------------
# API
# ----------------------------
@app.get("/api/health")
def health():
    data = get_cached_overview()
    return {
        "status": "ok",
        "cache_meta": data.get("_meta", {}),
        "app_env": APP_ENV,
    }


@app.get("/api/overview")
def overview():
    return get_cached_overview()


# ----------------------------
# WebSocket
# ----------------------------
@app.websocket("/ws/overview")
async def ws_overview(websocket: WebSocket):
    await websocket.accept()
    last_ts = None
    try:
        while True:
            data = get_cached_overview()
            cur_ts = data.get("_meta", {}).get("last_update_ts")
            if cur_ts != last_ts:
                await websocket.send_text(json.dumps(data, ensure_ascii=False))
                last_ts = cur_ts
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return


# ----------------------------
# 生产态静态托管
# ----------------------------
if IS_PROD:
    if DIST_ASSETS_DIR.exists():
        app.mount("/assets", StaticFiles(directory=str(DIST_ASSETS_DIR)), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """
        生产态下：
        - /                -> dist/index.html
        - /assets/...      -> 已由上面的 StaticFiles 托管
        - 其他前端路由       -> dist/index.html
        """
        index_file = DIST_DIR / "index.html"
        if not index_file.exists():
            raise HTTPException(
                status_code=500,
                detail=(
                    f"frontend build not found: {index_file}. "
                    "Please run `npm run build` in the frontend directory first."
                ),
            )
        return FileResponse(index_file)
else:
    @app.get("/")
    def dev_index_hint():
        return {
            "message": "Backend is running in development mode.",
            "frontend_dev_server": "Use Vite dev server, usually http://127.0.0.1:5173",
            "api_overview": "/api/overview",
            "ws_overview": "/ws/overview",
        }