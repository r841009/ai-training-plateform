import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.training_server import TrainingServer


class TrainingServerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, training_server: TrainingServer) -> TrainingServer:
        self.db.add(training_server)
        self.db.commit()
        self.db.refresh(training_server)
        return training_server

    def get(self, training_server_id: uuid.UUID) -> TrainingServer | None:
        return self.db.get(TrainingServer, training_server_id)

    def get_by_hostname(self, hostname: str) -> TrainingServer | None:
        return self.db.scalar(select(TrainingServer).where(TrainingServer.hostname == hostname))

    def list(self) -> list[TrainingServer]:
        return list(self.db.scalars(select(TrainingServer).order_by(TrainingServer.hostname)))

    def list_online(self) -> list[TrainingServer]:
        return list(
            self.db.scalars(select(TrainingServer).where(TrainingServer.status == "ONLINE").order_by(TrainingServer.hostname))
        )

    def save(self, training_server: TrainingServer) -> TrainingServer:
        self.db.commit()
        self.db.refresh(training_server)
        return training_server
