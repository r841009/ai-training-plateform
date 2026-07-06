import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import GUID


class TrainingJob(Base):
    __tablename__ = "training_jobs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("dataset_versions.id"), nullable=False, index=True
    )
    base_model_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("base_models.id"), nullable=False)
    trainer_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("trainer_registry.id"), nullable=False)
    assigned_server_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("training_servers.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING", index=True)
    resource_requirement_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    training_config_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
