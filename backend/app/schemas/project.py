import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    project_code: str = Field(min_length=1, max_length=64, pattern=r"^[A-Z0-9_]+$")
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    # project_code is immutable: it's baked into storage paths and model version names.
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_code: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
