import asyncio
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.queue import get_status

router = APIRouter(prefix="/stream", tags=["stream"])

_POLL_INTERVAL = 0.5
_TERMINAL = {"done", "failed"}


async def _event_generator(job_id: str):
    while True:
        job = get_status(job_id)
        if job is None:
            yield f"event: error\ndata: {json.dumps({'detail': 'job not found'})}\n\n"
            return

        data = {
            "job_id": job["job_id"],
            "status": job["status"],
            "progress": job.get("progress", 0),
        }
        if job.get("result"):
            data["result"] = job["result"]
        if job.get("error"):
            data["error"] = job["error"]

        yield f"data: {json.dumps(data)}\n\n"

        if job["status"] in _TERMINAL:
            yield "event: done\ndata: {}\n\n"
            return

        await asyncio.sleep(_POLL_INTERVAL)


@router.get("/{job_id}")
async def stream_job(job_id: str):
    job = get_status(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return StreamingResponse(
        _event_generator(job_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
