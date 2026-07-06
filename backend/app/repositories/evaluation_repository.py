import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.evaluation import EvaluationDataset, EvaluationResult


class EvaluationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_dataset(self, dataset: EvaluationDataset) -> EvaluationDataset:
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def get_dataset_for_project(
        self, project_id: uuid.UUID, evaluation_dataset_id: uuid.UUID
    ) -> EvaluationDataset | None:
        return self.db.scalar(
            select(EvaluationDataset).where(
                EvaluationDataset.id == evaluation_dataset_id,
                EvaluationDataset.project_id == project_id,
            )
        )

    def list_datasets_for_project(self, project_id: uuid.UUID) -> list[EvaluationDataset]:
        return list(
            self.db.scalars(
                select(EvaluationDataset)
                .where(EvaluationDataset.project_id == project_id)
                .order_by(EvaluationDataset.created_at.desc())
            )
        )

    def create_result(self, result: EvaluationResult) -> EvaluationResult:
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def list_results_for_project(self, project_id: uuid.UUID) -> list[EvaluationResult]:
        return list(
            self.db.scalars(
                select(EvaluationResult)
                .where(EvaluationResult.project_id == project_id)
                .order_by(EvaluationResult.created_at.desc())
            )
        )
