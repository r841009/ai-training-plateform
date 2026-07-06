import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.model_version import ModelVersion
from app.models.training_job import TrainingJob
from app.repositories.base_model_repository import BaseModelRepository
from app.repositories.model_version_repository import ModelVersionRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.training_job_repository import TrainingJobRepository
from app.schemas.training_job import TrainingJobCreate
from app.services.training_job_service import TrainingJobService


class ModelVersionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ModelVersionRepository(db)
        self.project_repo = ProjectRepository(db)
        self.base_model_repo = BaseModelRepository(db)
        self.training_job_repo = TrainingJobRepository(db)

    def list_model_versions(self, project_id: uuid.UUID) -> list[ModelVersion]:
        self._require_project(project_id)
        return self.repo.list_for_project(project_id)

    def get_model_version(self, project_id: uuid.UUID, model_version_id: uuid.UUID) -> ModelVersion:
        self._require_project(project_id)
        model_version = self.repo.get_for_project(project_id, model_version_id)
        if model_version is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "model version not found")
        return model_version

    def create_from_training_job(self, job: TrainingJob, artifact_path: str) -> ModelVersion:
        existing = self.repo.get_by_training_job(job.id)
        if existing is not None:
            return existing

        project = self._require_project(job.project_id)
        base_model = self.base_model_repo.get(job.base_model_id)
        if base_model is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "base model not found")

        parent_id = (job.training_config_json or {}).get("parent_model_version_id")
        if parent_id and self.repo.get_for_project(job.project_id, uuid.UUID(str(parent_id))) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "parent model version not found")

        version_no = self.repo.next_version_no(job.project_id)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        return self.repo.create(
            ModelVersion(
                project_id=job.project_id,
                training_job_id=job.id,
                dataset_version_id=job.dataset_version_id,
                base_model_id=job.base_model_id,
                parent_model_version_id=uuid.UUID(str(parent_id)) if parent_id else None,
                version_no=version_no,
                name=f"{project.project_code}_{base_model.name}_{timestamp}",
                artifact_path=artifact_path,
                metrics_json={},
            )
        )

    def retrain_model_version(self, project_id: uuid.UUID, model_version_id: uuid.UUID) -> TrainingJob:
        model_version = self.get_model_version(project_id, model_version_id)
        parent_job = self.training_job_repo.get_for_project(project_id, model_version.training_job_id)
        if parent_job is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "parent training job not found")

        training_config = dict(parent_job.training_config_json or {})
        training_config["parent_model_version_id"] = str(model_version.id)
        training_config.pop("resume", None)
        training_config.pop("checkpoint_latest_path", None)

        return TrainingJobService(self.db).create_training_job(
            project_id,
            TrainingJobCreate(
                dataset_version_id=model_version.dataset_version_id,
                base_model_id=model_version.base_model_id,
                trainer_id=parent_job.trainer_id,
                resource_requirement_json=parent_job.resource_requirement_json,
                training_config_json=training_config,
            ),
        )

    def _require_project(self, project_id: uuid.UUID):
        project = self.project_repo.get(project_id)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
        return project
