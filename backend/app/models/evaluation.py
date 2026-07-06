import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import GUID


class EvaluationDataset(Base):
    __tablename__ = "evaluation_datasets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    dataset_version_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("dataset_versions.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("projects.id"), nullable=False, index=True)
    model_version_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("model_versions.id"), nullable=False, index=True
    )
    dataset_version_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("dataset_versions.id"), nullable=True
    )
    evaluation_dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("evaluation_datasets.id"), nullable=True
    )
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sample_predictions_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
