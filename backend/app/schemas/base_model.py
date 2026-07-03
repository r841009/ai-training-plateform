import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseModelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    family: str
    task_type: str
    is_active: bool
    source_provider: str
    license_name: str
    license_url: str | None
    license_risk_level: str
    commercial_use_allowed: bool
    oem_use_allowed: bool
    requires_enterprise_license: bool
    license_notes: str | None
    created_at: datetime
