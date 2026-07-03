import json

from fastapi import APIRouter, Header, HTTPException, Response, status

from app.config import settings
from app.core.idempotency import idempotency_get, idempotency_set
from app.core.queue import JOB_PREFIX, enqueue, get_redis, get_status
from app.core.tracing import get_tracer, inject_trace_context
from app.models.schemas import JobCreate, JobStatus

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", status_code=status.HTTP_202_ACCEPTED, response_model=JobStatus)
async def submit_job(
    body: JobCreate,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    tracer = get_tracer()
    with tracer.start_as_current_span("api.submit_job") as span:
        if idempotency_key:
            existing_id = idempotency_get(idempotency_key)
            if existing_id:
                span.set_attribute("idempotency.hit", True)
                job = get_status(existing_id)
                if job:
                    return JobStatus(**job)

        trace_context = inject_trace_context()
        job_id = enqueue(body.payload)
        span.set_attribute("job.id", job_id)

        if idempotency_key:
            idempotency_set(idempotency_key, job_id)

        r = get_redis()
        raw = r.get(f"{JOB_PREFIX}{job_id}")
        if raw:
            data = json.loads(raw)
            data["trace_context"] = trace_context
            r.set(f"{JOB_PREFIX}{job_id}", json.dumps(data), ex=settings.job_ttl)

        response.headers["Location"] = f"/jobs/{job_id}"
        return JobStatus(job_id=job_id, status="queued")


@router.get("/{job_id}", response_model=JobStatus)
async def get_job(job_id: str):
    tracer = get_tracer()
    with tracer.start_as_current_span("api.get_job") as span:
        span.set_attribute("job.id", job_id)
        job = get_status(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        return JobStatus(**job)
