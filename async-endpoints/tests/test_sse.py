"""SSE stream tests."""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_job(job_id: str, status: str = "done", progress: int = 100, result=None):
    return {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "result": result or {"echo": {}},
        "error": None,
    }


def test_stream_unknown_job():
    with patch("app.routers.stream.get_status", return_value=None):
        resp = client.get("/stream/nonexistent")
    assert resp.status_code == 404


def test_stream_completed_job():
    job = _make_job("job-123", status="done", progress=100)

    with patch("app.routers.stream.get_status", return_value=job):
        with client.stream("GET", "/stream/job-123") as r:
            lines = []
            for line in r.iter_lines():
                lines.append(line)

    data_lines = [l for l in lines if l.startswith("data:")]
    assert len(data_lines) >= 1
    first = json.loads(data_lines[0][len("data:"):].strip())
    assert first["status"] == "done"
    assert first["progress"] == 100


def test_stream_progresses_to_done():
    states = [
        _make_job("j", status="running", progress=50, result=None),
        _make_job("j", status="done", progress=100),
    ]
    call_count = {"n": 0}

    def _get(job_id):
        idx = min(call_count["n"], len(states) - 1)
        call_count["n"] += 1
        return states[idx]

    with patch("app.routers.stream.get_status", side_effect=_get):
        with client.stream("GET", "/stream/j") as r:
            events = []
            for line in r.iter_lines():
                if line.startswith("data:") and line[5:].strip() not in ("", "{}"):
                    events.append(json.loads(line[5:].strip()))

    statuses = [e["status"] for e in events]
    assert "done" in statuses
