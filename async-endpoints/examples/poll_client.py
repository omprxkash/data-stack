"""Submit a job and poll until it finishes."""

import time

import httpx

BASE = "http://localhost:8000"


def main():
    resp = httpx.post(f"{BASE}/jobs", json={"payload": {"task": "hello", "value": 42}})
    resp.raise_for_status()
    job = resp.json()
    job_id = job["job_id"]
    print(f"Submitted job {job_id} — status: {job['status']}")

    while True:
        resp = httpx.get(f"{BASE}/jobs/{job_id}")
        resp.raise_for_status()
        data = resp.json()
        print(f"  status={data['status']}  progress={data['progress']}%")
        if data["status"] in ("done", "failed"):
            print("Result:", data.get("result") or data.get("error"))
            break
        time.sleep(0.5)


if __name__ == "__main__":
    main()
