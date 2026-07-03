import signal
import sys
import time

from app.config import settings
from app.core.queue import dequeue, set_status
from app.core.tracing import extract_trace_context, get_tracer

_running = True


def _handle_signal(signum, frame):
    global _running
    _running = False


def process_job(job: dict) -> None:
    tracer = get_tracer()
    carrier = job.get("trace_context", {})
    ctx = extract_trace_context(carrier)

    with tracer.start_as_current_span("worker.process_job", context=ctx) as span:
        job_id = job["job_id"]
        span.set_attribute("job.id", job_id)

        set_status(job_id, {"status": "running", "progress": 0})

        for step in range(1, 6):
            time.sleep(0.2)
            set_status(job_id, {"progress": step * 20})

        payload = job.get("payload", {})
        result = {"echo": payload, "steps_completed": 5}
        set_status(job_id, {"status": "done", "result": result, "progress": 100})
        span.set_attribute("job.status", "done")


def run_worker() -> None:
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    print("Worker started — waiting for jobs (poll interval: 2s)", flush=True)
    while _running:
        job = dequeue(timeout=2)
        if job is None:
            continue
        try:
            process_job(job)
            print(f"Completed job {job['job_id']}", flush=True)
        except Exception as exc:
            set_status(job["job_id"], {"status": "failed", "error": str(exc)})
            print(f"Job {job['job_id']} failed: {exc}", flush=True)


if __name__ == "__main__":
    run_worker()
