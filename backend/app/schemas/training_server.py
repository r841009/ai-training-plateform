import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.training_server import TRAINING_SERVER_STATUSES


class TrainingServerCreate(BaseModel):
    hostname: str = Field(min_length=1, max_length=255)
    ip_address: str | None = Field(default=None, max_length=64)
    max_concurrent_jobs: int = Field(default=1, ge=1)


class TrainingServerHeartbeat(BaseModel):
    status: str = "ONLINE"
    gpu_count: int = Field(default=0, ge=0)
    gpu_memory_total_gb: float = Field(default=0.0, ge=0)
    gpu_memory_free_gb: float = Field(default=0.0, ge=0)
    gpu_utilization_percent: float = Field(default=0.0, ge=0, le=100)
    cpu_usage_percent: float = Field(default=0.0, ge=0, le=100)
    ram_total_gb: float = Field(default=0.0, ge=0)
    ram_free_gb: float = Field(default=0.0, ge=0)
    disk_free_gb: float = Field(default=0.0, ge=0)
    running_job_count: int = Field(default=0, ge=0)
    max_concurrent_jobs: int | None = Field(default=None, ge=1)

    @field_validator("status")
    @classmethod
    def status_must_be_supported(cls, value: str) -> str:
        if value not in TRAINING_SERVER_STATUSES:
            allowed = ", ".join(TRAINING_SERVER_STATUSES)
            raise ValueError(f"status must be one of: {allowed}")
        return value


class TrainingServerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hostname: str
    ip_address: str | None
    status: str
    gpu_count: int
    gpu_memory_total_gb: float
    gpu_memory_free_gb: float
    gpu_utilization_percent: float
    cpu_usage_percent: float
    ram_total_gb: float
    ram_free_gb: float
    disk_free_gb: float
    running_job_count: int
    max_concurrent_jobs: int
    last_heartbeat_at: datetime | None
    created_at: datetime
    updated_at: datetime

