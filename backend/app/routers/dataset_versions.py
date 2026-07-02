import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.dataset_version import DatasetProcessRequest, DatasetVersionCreate, DatasetVersionRead
from app.schemas.response import ApiResponse, success_response
from app.services.dataset_version_service import DatasetVersionService

router = APIRouter(prefix="/projects/{project_id}/datasets", tags=["dataset-versions"])


def get_service(db: Session = Depends(get_db)) -> DatasetVersionService:
    return DatasetVersionService(db)


@router.post("", response_model=ApiResponse[DatasetVersionRead], status_code=201)
def create_dataset_version(
    project_id: uuid.UUID,
    payload: DatasetVersionCreate,
    service: DatasetVersionService = Depends(get_service),
):
    dataset_version = service.create_dataset_version(project_id, payload)
    return success_response(DatasetVersionRead.model_validate(dataset_version))


@router.get("", response_model=ApiResponse[list[DatasetVersionRead]])
def list_dataset_versions(project_id: uuid.UUID, service: DatasetVersionService = Depends(get_service)):
    dataset_versions = service.list_dataset_versions(project_id)
    return success_response([DatasetVersionRead.model_validate(d) for d in dataset_versions])


@router.get("/{dataset_version_id}", response_model=ApiResponse[DatasetVersionRead])
def get_dataset_version(
    project_id: uuid.UUID, dataset_version_id: uuid.UUID, service: DatasetVersionService = Depends(get_service)
):
    dataset_version = service.get_dataset_version(project_id, dataset_version_id)
    return success_response(DatasetVersionRead.model_validate(dataset_version))


@router.post("/{dataset_version_id}/upload", response_model=ApiResponse[DatasetVersionRead])
async def upload_dataset_zip(
    project_id: uuid.UUID,
    dataset_version_id: uuid.UUID,
    file: UploadFile = File(...),
    service: DatasetVersionService = Depends(get_service),
):
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(422, "only .zip uploads are supported")
    content = await file.read()
    dataset_version = service.ingest_zip(project_id, dataset_version_id, content)
    return success_response(DatasetVersionRead.model_validate(dataset_version))


@router.post("/{dataset_version_id}/process", response_model=ApiResponse[DatasetVersionRead])
def process_dataset_version(
    project_id: uuid.UUID,
    dataset_version_id: uuid.UUID,
    payload: DatasetProcessRequest = DatasetProcessRequest(),
    service: DatasetVersionService = Depends(get_service),
):
    dataset_version = service.process_dataset(project_id, dataset_version_id, payload)
    return success_response(DatasetVersionRead.model_validate(dataset_version))
