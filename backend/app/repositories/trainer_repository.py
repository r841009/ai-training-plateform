import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.trainer import Trainer


class TrainerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, trainer_id: uuid.UUID) -> Trainer | None:
        return self.db.get(Trainer, trainer_id)

    def list(self) -> list[Trainer]:
        return list(self.db.scalars(select(Trainer).order_by(Trainer.trainer_name)))
