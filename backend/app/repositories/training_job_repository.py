import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.training_job import TrainingJob


class TrainingJobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, training_job: TrainingJob) -> TrainingJob:
        self.db.add(training_job)
        self.db.commit()
        self.db.refresh(training_job)
        return training_job

    def get_for_project(self, project_id: uuid.UUID, training_job_id: uuid.UUID) -> TrainingJob | None:
        return self.db.scalar(
            select(TrainingJob).where(TrainingJob.id == training_job_id, TrainingJob.project_id == project_id)
        )

    def list_for_project(self, project_id: uuid.UUID) -> list[TrainingJob]:
        return list(
            self.db.scalars(
                select(TrainingJob).where(TrainingJob.project_id == project_id).order_by(TrainingJob.created_at.desc())
            )
        )

    def list_dispatch_candidates(self) -> list[TrainingJob]:
        return list(
            self.db.scalars(
                select(TrainingJob)
                .where(TrainingJob.status.in_(("PENDING", "QUEUED", "RESUMABLE")))
                .order_by(TrainingJob.created_at)
            )
        )

    def list_dispatched_for_server(self, server_id: uuid.UUID, limit: int = 1) -> list[TrainingJob]:
        return list(
            self.db.scalars(
                select(TrainingJob)
                .where(TrainingJob.status == "DISPATCHED", TrainingJob.assigned_server_id == server_id)
                .order_by(TrainingJob.created_at)
                .limit(limit)
            )
        )

    def save(self, training_job: TrainingJob) -> TrainingJob:
        self.db.commit()
        self.db.refresh(training_job)
        return training_job
