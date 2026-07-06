import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EvaluationDatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    dataset_version_id: uuid.UUID | None = None
    storage_path: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def requires_dataset_or_storage(self):
        if self.dataset_version_id is None and not self.storage_path:
            raise ValueError("dataset_version_id or storage_path is required")
        return self


class EvaluationDatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    dataset_version_id: uuid.UUID | None
    name: str
    storage_path: str | None
    description: str | None
    created_at: datetime


class EvaluationRunRequest(BaseModel):
    evaluation_dataset_id: uuid.UUID | None = None


class EvaluationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    model_version_id: uuid.UUID
    dataset_version_id: uuid.UUID | None
    evaluation_dataset_id: uuid.UUID | None
    metrics_json: dict[str, Any]
    report_path: str | None
    sample_predictions_path: str | None
    created_at: datetime
