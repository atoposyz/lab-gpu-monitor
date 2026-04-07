import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.services.cache import get_cached_overview

router = APIRouter(prefix="/api")


@router.get("/overview")
def overview():
    return get_cached_overview()


@router.websocket("/ws/overview")
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
