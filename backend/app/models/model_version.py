import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import GUID


class ModelVersion(Base):
    __tablename__ = "model_versions"
    __table_args__ = (
        UniqueConstraint("project_id", "version_no", name="uq_model_versions_project_version"),
        UniqueConstraint("training_job_id", name="uq_model_versions_training_job"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    training_job_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("training_jobs.id"), nullable=False, index=True
    )
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("dataset_versions.id"), nullable=False)
    base_model_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("base_models.id"), nullable=False)
    parent_model_version_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("model_versions.id"), nullable=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    artifact_path: Mapped[str] = mapped_column(String(500), nullable=False)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
