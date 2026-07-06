import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.response import ApiResponse, success_response
from app.schemas.training_job import TrainingJobCreate, TrainingJobRead
from app.services.training_job_service import TrainingJobService

router = APIRouter(prefix="/projects/{project_id}/training-jobs", tags=["training-jobs"])


def get_service(db: Session = Depends(get_db)) -> TrainingJobService:
    return TrainingJobService(db)


@router.post("", response_model=ApiResponse[TrainingJobRead], status_code=201)
def create_training_job(
    project_id: uuid.UUID,
    payload: TrainingJobCreate,
    service: TrainingJobService = Depends(get_service),
):
    training_job = service.create_training_job(project_id, payload)
    return success_response(TrainingJobRead.model_validate(training_job))


@router.get("", response_model=ApiResponse[list[TrainingJobRead]])
def list_training_jobs(project_id: uuid.UUID, service: TrainingJobService = Depends(get_service)):
    training_jobs = service.list_training_jobs(project_id)
    return success_response([TrainingJobRead.model_validate(j) for j in training_jobs])


@router.get("/{training_job_id}", response_model=ApiResponse[TrainingJobRead])
def get_training_job(
    project_id: uuid.UUID,
    training_job_id: uuid.UUID,
    service: TrainingJobService = Depends(get_service),
):
    training_job = service.get_training_job(project_id, training_job_id)
    return success_response(TrainingJobRead.model_validate(training_job))


@router.post("/{training_job_id}/resume", response_model=ApiResponse[TrainingJobRead])
def resume_training_job(
    project_id: uuid.UUID,
    training_job_id: uuid.UUID,
    service: TrainingJobService = Depends(get_service),
):
    return success_response(TrainingJobRead.model_validate(service.resume_training_job(project_id, training_job_id)))
