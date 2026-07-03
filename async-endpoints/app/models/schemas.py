from typing import Literal
from pydantic import BaseModel


class JobCreate(BaseModel):
    payload: dict


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "running", "done", "failed"]
    result: dict | None = None
    error: str | None = None
    progress: int = 0
