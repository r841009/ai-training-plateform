import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrainerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    trainer_name: str
    task_type: str
    base_model_family: str
    entrypoint: str
    docker_image: str | None
    supported_resume: bool
    supported_export_formats: list[str] | None
    is_active: bool
    created_at: datetime
