import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ModelVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    training_job_id: uuid.UUID
    dataset_version_id: uuid.UUID
    base_model_id: uuid.UUID
    parent_model_version_id: uuid.UUID | None
    version_no: int
    name: str
    artifact_path: str
    metrics_json: dict[str, Any]
    created_at: datetime
