import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import GUID


class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    training_job_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("training_jobs.id"), nullable=False, index=True
    )
    checkpoint_path: Mapped[str] = mapped_column(String(500), nullable=False)
    epoch: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_latest: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_best: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
