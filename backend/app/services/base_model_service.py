import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.base_model import BaseModelEntry
from app.repositories.base_model_repository import BaseModelRepository


class BaseModelService:
    def __init__(self, db: Session):
        self.repo = BaseModelRepository(db)

    def get_base_model(self, base_model_id: uuid.UUID) -> BaseModelEntry:
        base_model = self.repo.get(base_model_id)
        if base_model is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "base model not found")
        return base_model

    def list_base_models(self) -> list[BaseModelEntry]:
        return self.repo.list()
