import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.queue import get_status

router = APIRouter(tags=["websocket"])

_POLL_INTERVAL = 0.5
_HEARTBEAT_INTERVAL = 15.0  # seconds between keep-alive pings
_TERMINAL = {"done", "failed"}


@router.websocket("/ws/jobs/{job_id}")
async def ws_job(websocket: WebSocket, job_id: str):
    await websocket.accept()

    job = get_status(job_id)
    if job is None:
        await websocket.send_text(json.dumps({"error": "job not found"}))
        await websocket.close(code=1008)
        return

    try:
        last_heartbeat = asyncio.get_event_loop().time()

        while True:
            job = get_status(job_id)
            if job is None:
                await websocket.send_text(json.dumps({"error": "job disappeared"}))
                break

            payload = {
                "job_id": job["job_id"],
                "status": job["status"],
                "progress": job.get("progress", 0),
            }
            if job.get("result"):
                payload["result"] = job["result"]
            if job.get("error"):
                payload["error"] = job["error"]

            await websocket.send_text(json.dumps(payload))

            if job["status"] in _TERMINAL:
                break

            now = asyncio.get_event_loop().time()
            if now - last_heartbeat >= _HEARTBEAT_INTERVAL:
                await websocket.send_text(json.dumps({"ping": True}))
                last_heartbeat = now

            await asyncio.sleep(_POLL_INTERVAL)

    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
