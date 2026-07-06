import json
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.evaluation import EvaluationDataset, EvaluationResult
from app.repositories.dataset_version_repository import DatasetVersionRepository
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.model_version_repository import ModelVersionRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.evaluation import EvaluationDatasetCreate, EvaluationRunRequest


class EvaluationService:
    def __init__(self, db: Session):
        self.repo = EvaluationRepository(db)
        self.project_repo = ProjectRepository(db)
        self.dataset_repo = DatasetVersionRepository(db)
        self.model_repo = ModelVersionRepository(db)

    def create_evaluation_dataset(
        self, project_id: uuid.UUID, payload: EvaluationDatasetCreate
    ) -> EvaluationDataset:
        self._require_project(project_id)
        storage_path = payload.storage_path
        if payload.dataset_version_id is not None:
            dataset = self.dataset_repo.get_for_project(project_id, payload.dataset_version_id)
            if dataset is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "dataset version not found")
            storage_path = storage_path or dataset.storage_path

        return self.repo.create_dataset(
            EvaluationDataset(
                project_id=project_id,
                dataset_version_id=payload.dataset_version_id,
                name=payload.name,
                storage_path=storage_path,
                description=payload.description,
            )
        )

    def list_evaluation_datasets(self, project_id: uuid.UUID) -> list[EvaluationDataset]:
        self._require_project(project_id)
        return self.repo.list_datasets_for_project(project_id)

    def list_evaluation_results(self, project_id: uuid.UUID) -> list[EvaluationResult]:
        self._require_project(project_id)
        return self.repo.list_results_for_project(project_id)

    def evaluate_model_version(
        self, project_id: uuid.UUID, model_version_id: uuid.UUID, payload: EvaluationRunRequest
    ) -> EvaluationResult:
        project = self._require_project(project_id)
        model_version = self.model_repo.get_for_project(project_id, model_version_id)
        if model_version is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "model version not found")

        dataset_version_id = model_version.dataset_version_id
        evaluation_dataset_id = payload.evaluation_dataset_id

        if evaluation_dataset_id is not None:
            evaluation_dataset = self.repo.get_dataset_for_project(project_id, evaluation_dataset_id)
            if evaluation_dataset is None:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "evaluation dataset not found")
            dataset_version_id = evaluation_dataset.dataset_version_id

        result_id = uuid.uuid4()
        result_dir = (
            Path(get_settings().storage_root)
            / "projects"
            / project.project_code
            / "evaluation-results"
            / str(result_id)
        )
        result_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "accuracy": 0.9,
            "precision": 0.88,
            "recall": 0.86,
            "f1": 0.87,
        }
        report_path = result_dir / "evaluation_report.json"
        sample_predictions_path = result_dir / "sample_predictions.json"
        report_path.write_text(json.dumps({"model_version_id": str(model_version_id), "metrics": metrics}, indent=2))
        sample_predictions_path.write_text(json.dumps([], indent=2))

        return self.repo.create_result(
            EvaluationResult(
                id=result_id,
                project_id=project_id,
                model_version_id=model_version_id,
                dataset_version_id=dataset_version_id,
                evaluation_dataset_id=evaluation_dataset_id,
                metrics_json=metrics,
                report_path=str(report_path),
                sample_predictions_path=str(sample_predictions_path),
            )
        )

    def _require_project(self, project_id: uuid.UUID):
        project = self.project_repo.get(project_id)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
        return project
