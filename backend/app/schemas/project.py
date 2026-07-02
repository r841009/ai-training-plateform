import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

PROJECT_CODE_PATTERN = re.compile(r"^[A-Z0-9_]+$")


class ProjectCreate(BaseModel):
    project_code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

    @field_validator("project_code")
    @classmethod
    def validate_project_code(cls, v: str) -> str:
        if not PROJECT_CODE_PATTERN.match(v):
            raise ValueError("project_code must contain only uppercase letters, digits, or underscore")
        return v


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
