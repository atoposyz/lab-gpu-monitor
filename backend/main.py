import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api import admin as admin_api
from backend.api import announcements as announcements_api
from backend.api import auth as auth_api
from backend.api import applications as applications_api
from backend.api import health as health_api
from backend.api import overview as overview_api
from backend.core.config import settings
from backend.core.logging import configure_logging
from backend.db.base import Base
from backend.db.session import engine
from backend.services.cache import get_cached_overview, start_background_refresh

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
DIST_DIR = os.path.join(FRONTEND_DIR, "dist")
DIST_ASSETS_DIR = os.path.join(DIST_DIR, "assets")

APP_ENV = os.getenv("APP_ENV", "dev").lower()
IS_PROD = APP_ENV == "prod"


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    Base.metadata.create_all(bind=engine)
    start_background_refresh()
    yield


app = FastAPI(title="Lab GPU Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_api.router)
app.include_router(overview_api.router)
app.include_router(auth_api.router)
app.include_router(applications_api.router)
app.include_router(admin_api.router)
app.include_router(announcements_api.router)

if IS_PROD:
    if os.path.exists(DIST_ASSETS_DIR):
        app.mount("/assets", StaticFiles(directory=DIST_ASSETS_DIR), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        index_file = os.path.join(DIST_DIR, "index.html")
        if not os.path.exists(index_file):
            raise HTTPException(
                status_code=500,
                detail=(
                    f"frontend build not found: {index_file}. Please run `npm run build` in frontend first."
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
