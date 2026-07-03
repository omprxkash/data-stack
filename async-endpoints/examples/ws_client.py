"""Submit a job and stream its status over a WebSocket."""

import asyncio
import json

import httpx
import websockets

BASE_HTTP = "http://localhost:8000"
BASE_WS = "ws://localhost:8000"


async def main():
    resp = httpx.post(f"{BASE_HTTP}/jobs", json={"payload": {"mode": "ws-demo"}})
    resp.raise_for_status()
    job_id = resp.json()["job_id"]
    print(f"Submitted job {job_id}, connecting to WebSocket…")

    async with websockets.connect(f"{BASE_WS}/ws/jobs/{job_id}") as ws:
        async for message in ws:
            data = json.loads(message)
            if data.get("ping"):
                continue
            print(f"  status={data.get('status')}  progress={data.get('progress')}%")
            if data.get("status") in ("done", "failed"):
                print("Final result:", data.get("result") or data.get("error"))
                break


if __name__ == "__main__":
    asyncio.run(main())
