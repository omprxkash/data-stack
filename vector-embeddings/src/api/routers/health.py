from fastapi import APIRouter
import time

router = APIRouter()
_start = time.time()


@router.get("/health")
def health():
    return {"status": "ok", "uptime_seconds": round(time.time() - _start)}
