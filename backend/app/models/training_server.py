import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import GUID

TRAINING_SERVER_STATUSES = ("REGISTERED", "ONLINE", "OFFLINE", "DRAINING", "UNAVAILABLE")


class TrainingServer(Base):
    __tablename__ = "training_servers"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    hostname: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="REGISTERED")
    gpu_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gpu_memory_total_gb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gpu_memory_free_gb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gpu_utilization_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cpu_usage_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ram_total_gb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    ram_free_gb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    disk_free_gb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    running_job_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_concurrent_jobs: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

