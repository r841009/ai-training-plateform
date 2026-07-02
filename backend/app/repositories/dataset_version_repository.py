import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.dataset_version import DatasetVersion


class DatasetVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, dataset_version: DatasetVersion) -> DatasetVersion:
        self.db.add(dataset_version)
        self.db.commit()
        self.db.refresh(dataset_version)
        return dataset_version

    def get_for_project(self, project_id: uuid.UUID, dataset_version_id: uuid.UUID) -> DatasetVersion | None:
        return self.db.scalar(
            select(DatasetVersion).where(
                DatasetVersion.id == dataset_version_id, DatasetVersion.project_id == project_id
            )
        )

    def list_for_project(self, project_id: uuid.UUID) -> list[DatasetVersion]:
        return list(
            self.db.scalars(
                select(DatasetVersion)
                .where(DatasetVersion.project_id == project_id)
                .order_by(DatasetVersion.version_no)
            )
        )

    def next_version_no(self, project_id: uuid.UUID) -> int:
        current_max = self.db.scalar(
            select(func.max(DatasetVersion.version_no)).where(DatasetVersion.project_id == project_id)
        )
        return (current_max or 0) + 1

    def save(self, dataset_version: DatasetVersion) -> DatasetVersion:
        self.db.commit()
        self.db.refresh(dataset_version)
        return dataset_version
