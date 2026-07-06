from sqlalchemy.orm import Session

from app.models.checkpoint import Checkpoint


class CheckpointRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, checkpoint: Checkpoint) -> Checkpoint:
        self.db.add(checkpoint)
        self.db.commit()
        self.db.refresh(checkpoint)
        return checkpoint
