import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.training_job import TrainingJob
from app.repositories.base_model_repository import BaseModelRepository
from app.repositories.dataset_version_repository import DatasetVersionRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.trainer_repository import TrainerRepository
from app.repositories.training_job_repository import TrainingJobRepository
from app.schemas.training_job import TrainingJobCreate


class TrainingJobService:
    def __init__(self, db: Session):
        self.repo = TrainingJobRepository(db)
        self.project_repo = ProjectRepository(db)
        self.dataset_repo = DatasetVersionRepository(db)
        self.base_model_repo = BaseModelRepository(db)
        self.trainer_repo = TrainerRepository(db)

    def _require_project(self, project_id: uuid.UUID):
        project = self.project_repo.get(project_id)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
        return project

    def create_training_job(self, project_id: uuid.UUID, payload: TrainingJobCreate) -> TrainingJob:
        self._require_project(project_id)

        dataset_version = self.dataset_repo.get_for_project(project_id, payload.dataset_version_id)
        if dataset_version is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "dataset version not found")
        if dataset_version.status != "READY":
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"dataset version must be READY before training, current status is {dataset_version.status}",
            )

        base_model = self.base_model_repo.get(payload.base_model_id)
        if base_model is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "base model not found")

        trainer = self.trainer_repo.get(payload.trainer_id)
        if trainer is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "trainer not found")

        training_job = TrainingJob(
            project_id=project_id,
            dataset_version_id=payload.dataset_version_id,
            base_model_id=payload.base_model_id,
            trainer_id=payload.trainer_id,
            status="PENDING",
            resource_requirement_json=payload.resource_requirement_json,
            training_config_json=payload.training_config_json,
        )
        return self.repo.create(training_job)

    def get_training_job(self, project_id: uuid.UUID, training_job_id: uuid.UUID) -> TrainingJob:
        self._require_project(project_id)
        training_job = self.repo.get_for_project(project_id, training_job_id)
        if training_job is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "training job not found")
        return training_job

    def list_training_jobs(self, project_id: uuid.UUID) -> list[TrainingJob]:
        self._require_project(project_id)
        return self.repo.list_for_project(project_id)

