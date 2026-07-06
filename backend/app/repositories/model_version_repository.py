import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion


class ModelVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, model_version: ModelVersion) -> ModelVersion:
        self.db.add(model_version)
        self.db.commit()
        self.db.refresh(model_version)
        return model_version

    def get_for_project(self, project_id: uuid.UUID, model_version_id: uuid.UUID) -> ModelVersion | None:
        return self.db.scalar(
            select(ModelVersion).where(ModelVersion.id == model_version_id, ModelVersion.project_id == project_id)
        )

    def get_by_training_job(self, training_job_id: uuid.UUID) -> ModelVersion | None:
        return self.db.scalar(select(ModelVersion).where(ModelVersion.training_job_id == training_job_id))

    def list_for_project(self, project_id: uuid.UUID) -> list[ModelVersion]:
        return list(
            self.db.scalars(
                select(ModelVersion).where(ModelVersion.project_id == project_id).order_by(ModelVersion.version_no.desc())
            )
        )

    def next_version_no(self, project_id: uuid.UUID) -> int:
        current = self.db.scalar(select(func.max(ModelVersion.version_no)).where(ModelVersion.project_id == project_id))
        return int(current or 0) + 1
