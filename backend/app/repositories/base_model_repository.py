import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base_model import BaseModelEntry


class BaseModelRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, base_model_id: uuid.UUID) -> BaseModelEntry | None:
        return self.db.get(BaseModelEntry, base_model_id)

    def list(self) -> list[BaseModelEntry]:
        return list(self.db.scalars(select(BaseModelEntry).order_by(BaseModelEntry.name)))
