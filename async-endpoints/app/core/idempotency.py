import redis

from app.config import settings

IDEMPOTENCY_PREFIX = "idempotency:"


def _redis() -> redis.Redis:
    return redis.from_url(settings.redis_url, decode_responses=True)


def idempotency_get(key: str) -> str | None:
    """Return the job_id previously stored for this key, or None."""
    return _redis().get(f"{IDEMPOTENCY_PREFIX}{key}")


def idempotency_set(key: str, job_id: str, ttl: int = 86400) -> None:
    _redis().set(f"{IDEMPOTENCY_PREFIX}{key}", job_id, ex=ttl)
