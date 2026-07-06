import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.model_version import ModelVersionRead
from app.schemas.response import ApiResponse, success_response
from app.schemas.training_job import TrainingJobRead
from app.services.model_version_service import ModelVersionService

router = APIRouter(prefix="/projects/{project_id}/model-versions", tags=["model-versions"])


def get_service(db: Session = Depends(get_db)) -> ModelVersionService:
    return ModelVersionService(db)


@router.get("", response_model=ApiResponse[list[ModelVersionRead]])
def list_model_versions(project_id: uuid.UUID, service: ModelVersionService = Depends(get_service)):
    return success_response([ModelVersionRead.model_validate(m) for m in service.list_model_versions(project_id)])


@router.get("/{model_version_id}", response_model=ApiResponse[ModelVersionRead])
def get_model_version(
    project_id: uuid.UUID,
    model_version_id: uuid.UUID,
    service: ModelVersionService = Depends(get_service),
):
    return success_response(ModelVersionRead.model_validate(service.get_model_version(project_id, model_version_id)))


@router.post("/{model_version_id}/retrain", response_model=ApiResponse[TrainingJobRead], status_code=201)
def retrain_model_version(
    project_id: uuid.UUID,
    model_version_id: uuid.UUID,
    service: ModelVersionService = Depends(get_service),
):
    return success_response(TrainingJobRead.model_validate(service.retrain_model_version(project_id, model_version_id)))
