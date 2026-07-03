from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.tracing import setup_tracing
from app.routers import jobs, stream, websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_tracing()
    yield


app = FastAPI(
    title="async-endpoints",
    description="Reference implementation of async API patterns: 202+poll, SSE, WebSockets, circuit breaker, retry, idempotency, and distributed tracing.",
    version="1.0.0",
    license_info={"name": "MIT"},
    lifespan=lifespan,
)

app.include_router(jobs.router)
app.include_router(stream.router)
app.include_router(websocket.router)


@app.get("/healthz", tags=["health"])
async def healthz():
    return {"status": "ok"}
