from fastapi import APIRouter

from backend.services.cache import get_cached_overview
from backend.core.config import settings

router = APIRouter(prefix="/api")


@router.get("/health")
def health():
    data = get_cached_overview()
    return {
        "status": "ok",
        "cache_meta": data.get("_meta", {}),
        "app_env": settings.app_env,
    }
