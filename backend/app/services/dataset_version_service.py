import tempfile
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.dataset_processing import finalize_dataset, validate_dataset, write_invalid_report
from app.models.dataset_version import DatasetVersion
from app.repositories.dataset_version_repository import DatasetVersionRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.dataset_version import DatasetProcessRequest, DatasetVersionCreate
from app.storage import dataset_storage_path, ensure_dataset_dirs, safe_extract_zip

UPLOADABLE_STATUSES = {"CREATED", "UPLOADED"}
PROCESSABLE_STATUSES = {"UPLOADED"}


class DatasetVersionService:
    def __init__(self, db: Session):
        self.repo = DatasetVersionRepository(db)
        self.project_repo = ProjectRepository(db)

    def _require_project(self, project_id: uuid.UUID):
        project = self.project_repo.get(project_id)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
        return project

    def create_dataset_version(self, project_id: uuid.UUID, payload: DatasetVersionCreate) -> DatasetVersion:
        project = self._require_project(project_id)
        version_no = self.repo.next_version_no(project_id)
        storage_path = dataset_storage_path(project.project_code, version_no)
        ensure_dataset_dirs(storage_path)

        dataset_version = DatasetVersion(
            project_id=project_id,
            version_no=version_no,
            status="CREATED",
            storage_path=str(storage_path),
            description=payload.description,
        )
        return self.repo.create(dataset_version)

    def get_dataset_version(self, project_id: uuid.UUID, dataset_version_id: uuid.UUID) -> DatasetVersion:
        self._require_project(project_id)
        dataset_version = self.repo.get_for_project(project_id, dataset_version_id)
        if dataset_version is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "dataset version not found")
        return dataset_version

    def list_dataset_versions(self, project_id: uuid.UUID) -> list[DatasetVersion]:
        self._require_project(project_id)
        return self.repo.list_for_project(project_id)

    def ingest_zip(self, project_id: uuid.UUID, dataset_version_id: uuid.UUID, content: bytes) -> DatasetVersion:
        dataset_version = self.get_dataset_version(project_id, dataset_version_id)
        if dataset_version.status not in UPLOADABLE_STATUSES:
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"cannot upload while status is {dataset_version.status}"
            )

        previous_status = dataset_version.status
        dataset_version.status = "UPLOADING"
        self.repo.save(dataset_version)

        raw_dir = Path(dataset_version.storage_path) / "raw"
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(content)
                tmp_path = Path(tmp.name)
            safe_extract_zip(tmp_path, raw_dir)
        except Exception as exc:
            dataset_version.status = previous_status
            self.repo.save(dataset_version)
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"invalid zip upload: {exc}") from exc
        finally:
            if tmp_path is not None:
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass

        dataset_version.status = "UPLOADED"
        return self.repo.save(dataset_version)

    def process_dataset(
        self, project_id: uuid.UUID, dataset_version_id: uuid.UUID, payload: DatasetProcessRequest
    ) -> DatasetVersion:
        dataset_version = self.get_dataset_version(project_id, dataset_version_id)
        if dataset_version.status not in PROCESSABLE_STATUSES:
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"cannot process while status is {dataset_version.status}"
            )

        dataset_version.status = "VALIDATING"
        self.repo.save(dataset_version)

        storage_path = Path(dataset_version.storage_path)
        outcome = validate_dataset(storage_path)

        if not outcome.manifest_entries:
            write_invalid_report(storage_path, dataset_version.id, outcome)
            dataset_version.status = "INVALID"
            return self.repo.save(dataset_version)

        dataset_version.status = "PROCESSING"
        self.repo.save(dataset_version)

        finalize_dataset(
            storage_path, dataset_version.id, outcome, payload.class_names, payload.train_ratio, payload.val_ratio
        )

        dataset_version.status = "READY"
        return self.repo.save(dataset_version)
