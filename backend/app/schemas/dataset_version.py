import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class DatasetVersionCreate(BaseModel):
    description: str | None = None


class DatasetProcessRequest(BaseModel):
    class_names: dict[int, str] | None = None
    train_ratio: float = 0.7
    val_ratio: float = 0.2
    test_ratio: float = 0.1

    @model_validator(mode="after")
    def check_ratios_sum_to_one(self) -> "DatasetProcessRequest":
        total = self.train_ratio + self.val_ratio + self.test_ratio
        if abs(total - 1.0) > 1e-6:
            raise ValueError("train_ratio + val_ratio + test_ratio must sum to 1.0")
        return self


class DatasetVersionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    version_no: int
    status: str
    storage_path: str
    description: str | None
    created_at: datetime
    updated_at: datetime
