"""Job lifecycle and idempotency tests."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Replace Redis with an in-memory dict for all job tests."""
    store: dict = {}
    queue: list = []

    import app.core.queue as q
    import app.core.idempotency as idem

    original_enqueue = q.enqueue
    original_dequeue = q.dequeue
    original_get_status = q.get_status
    original_set_status = q.set_status
    original_get_redis = q.get_redis
    original_idem_get = idem.idempotency_get
    original_idem_set = idem.idempotency_set

    import uuid, json

    def _enqueue(payload, job_id=None):
        job_id = job_id or str(uuid.uuid4())
        store[job_id] = {"job_id": job_id, "status": "queued", "payload": payload, "progress": 0}
        queue.append(job_id)
        return job_id

    def _get_status(job_id):
        return dict(store[job_id]) if job_id in store else None

    def _set_status(job_id, updates):
        if job_id in store:
            store[job_id].update(updates)

    idempotency_store: dict = {}

    def _idem_get(key):
        return idempotency_store.get(key)

    def _idem_set(key, job_id, ttl=86400):
        idempotency_store[key] = job_id

    fake_redis = MagicMock()

    def _get_redis():
        return fake_redis

    fake_redis.get.side_effect = lambda k: json.dumps(store[k.split(":", 1)[1]]) if k.split(":", 1)[1] in store else None
    fake_redis.set.side_effect = lambda k, v, ex=None: store.update({k.split(":", 1)[1]: json.loads(v)})

    monkeypatch.setattr(q, "enqueue", _enqueue)
    monkeypatch.setattr(q, "get_status", _get_status)
    monkeypatch.setattr(q, "set_status", _set_status)
    monkeypatch.setattr(q, "get_redis", _get_redis)
    monkeypatch.setattr(idem, "idempotency_get", _idem_get)
    monkeypatch.setattr(idem, "idempotency_set", _idem_set)

    yield store, idempotency_store


def test_submit_returns_202():
    resp = client.post("/jobs", json={"payload": {"x": 1}})
    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "queued"
    assert "job_id" in data
    assert resp.headers["location"].startswith("/jobs/")


def test_get_job_status(mock_redis):
    store, _ = mock_redis
    resp = client.post("/jobs", json={"payload": {"x": 2}})
    job_id = resp.json()["job_id"]

    resp2 = client.get(f"/jobs/{job_id}")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "queued"


def test_get_unknown_job():
    resp = client.get("/jobs/does-not-exist")
    assert resp.status_code == 404


def test_idempotency_key_deduplicates(mock_redis):
    store, idem_store = mock_redis
    headers = {"Idempotency-Key": "test-key-123"}

    r1 = client.post("/jobs", json={"payload": {"y": 1}}, headers=headers)
    r2 = client.post("/jobs", json={"payload": {"y": 1}}, headers=headers)

    assert r1.status_code == 202
    assert r2.status_code == 202
    assert r1.json()["job_id"] == r2.json()["job_id"]


def test_different_idempotency_keys_create_different_jobs():
    r1 = client.post("/jobs", json={"payload": {}}, headers={"Idempotency-Key": "key-a"})
    r2 = client.post("/jobs", json={"payload": {}}, headers={"Idempotency-Key": "key-b"})
    assert r1.json()["job_id"] != r2.json()["job_id"]


def test_location_header_on_submit():
    resp = client.post("/jobs", json={"payload": {"check": "location"}})
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]
    assert resp.headers.get("location") == f"/jobs/{job_id}"
