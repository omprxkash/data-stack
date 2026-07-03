"""Submit a job and watch it over Server-Sent Events."""

import json

import httpx

BASE = "http://localhost:8000"


def main():
    resp = httpx.post(f"{BASE}/jobs", json={"payload": {"mode": "sse-demo"}})
    resp.raise_for_status()
    job_id = resp.json()["job_id"]
    print(f"Submitted job {job_id}, subscribing to SSE stream…")

    with httpx.stream("GET", f"{BASE}/stream/{job_id}") as r:
        for line in r.iter_lines():
            if not line.startswith("data:"):
                continue
            raw = line[len("data:"):].strip()
            if not raw or raw == "{}":
                continue
            event = json.loads(raw)
            print(f"  status={event.get('status')}  progress={event.get('progress')}%")
            if event.get("status") in ("done", "failed"):
                print("Final result:", event.get("result") or event.get("error"))
                break


if __name__ == "__main__":
    main()
