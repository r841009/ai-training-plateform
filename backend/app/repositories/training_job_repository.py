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

