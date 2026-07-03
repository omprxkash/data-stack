import json
import uuid

import redis

from app.config import settings

QUEUE_KEY = "jobs:queue"
JOB_PREFIX = "job:"


def get_redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def enqueue(payload: dict, job_id: str | None = None) -> str:
    r = get_redis()
    job_id = job_id or str(uuid.uuid4())
    job_data = {"job_id": job_id, "status": "queued", "payload": payload, "progress": 0}
    r.set(f"{JOB_PREFIX}{job_id}", json.dumps(job_data), ex=settings.job_ttl)
    r.rpush(QUEUE_KEY, job_id)
    return job_id


def dequeue(timeout: int = 2) -> dict | None:
    r = get_redis()
    result = r.blpop(QUEUE_KEY, timeout=timeout)
    if not result:
        return None
    _, job_id = result
    raw = r.get(f"{JOB_PREFIX}{job_id}")
    if not raw:
        return None
    return json.loads(raw)


def get_status(job_id: str) -> dict | None:
    r = get_redis()
    raw = r.get(f"{JOB_PREFIX}{job_id}")
    return json.loads(raw) if raw else None


def set_status(job_id: str, updates: dict) -> None:
    r = get_redis()
    key = f"{JOB_PREFIX}{job_id}"
    raw = r.get(key)
    if not raw:
        return
    data = json.loads(raw)
    data.update(updates)
    r.set(key, json.dumps(data), ex=settings.job_ttl)


def clear_queue() -> int:
    r = get_redis()
    return r.delete(QUEUE_KEY)
