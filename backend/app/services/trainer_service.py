import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.trainer import Trainer
from app.repositories.trainer_repository import TrainerRepository


class TrainerService:
    def __init__(self, db: Session):
        self.repo = TrainerRepository(db)

    def get_trainer(self, trainer_id: uuid.UUID) -> Trainer:
        trainer = self.repo.get(trainer_id)
        if trainer is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "trainer not found")
        return trainer

    def list_trainers(self) -> list[Trainer]:
        return self.repo.list()
