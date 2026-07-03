import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TrainingJobCreate(BaseModel):
    dataset_version_id: uuid.UUID
    base_model_id: uuid.UUID
    trainer_id: uuid.UUID
    resource_requirement_json: dict[str, Any] = Field(default_factory=dict)
    training_config_json: dict[str, Any] = Field(default_factory=dict)


class TrainingJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    dataset_version_id: uuid.UUID
    base_model_id: uuid.UUID
    trainer_id: uuid.UUID
    assigned_server_id: uuid.UUID | None
    status: str
    resource_requirement_json: dict[str, Any]
    training_config_json: dict[str, Any]
    failure_reason: str | None
    created_at: datetime
    updated_at: datetime

