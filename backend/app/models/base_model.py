import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.types import GUID


class BaseModelEntry(Base):
    # Named "Entry" (not "BaseModel") to avoid clashing with pydantic.BaseModel.
    __tablename__ = "base_models"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    family: Mapped[str] = mapped_column(String(64), nullable=False)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_provider: Mapped[str] = mapped_column(String(128), nullable=False, default="unknown")
    license_name: Mapped[str] = mapped_column(String(128), nullable=False, default="UNKNOWN")
    license_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    license_risk_level: Mapped[str] = mapped_column(String(32), nullable=False, default="UNKNOWN")
    commercial_use_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    oem_use_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_enterprise_license: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    license_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
