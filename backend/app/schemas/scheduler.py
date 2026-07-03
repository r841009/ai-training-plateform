import uuid

from pydantic import BaseModel


class DispatchDecision(BaseModel):
    training_job_id: uuid.UUID
    status: str
    assigned_server_id: uuid.UUID | None = None
    reason: str | None = None


class DispatchSummary(BaseModel):
    scanned: int
    dispatched: int
    queued: int
    failed: int
    decisions: list[DispatchDecision]

