import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.evaluation import (
    EvaluationDatasetCreate,
    EvaluationDatasetRead,
    EvaluationResultRead,
    EvaluationRunRequest,
)
from app.schemas.response import ApiResponse, success_response
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/projects/{project_id}", tags=["evaluations"])


def get_service(db: Session = Depends(get_db)) -> EvaluationService:
    return EvaluationService(db)


@router.post("/evaluation-datasets", response_model=ApiResponse[EvaluationDatasetRead], status_code=201)
def create_evaluation_dataset(
    project_id: uuid.UUID,
    payload: EvaluationDatasetCreate,
    service: EvaluationService = Depends(get_service),
):
    return success_response(EvaluationDatasetRead.model_validate(service.create_evaluation_dataset(project_id, payload)))


@router.get("/evaluation-datasets", response_model=ApiResponse[list[EvaluationDatasetRead]])
def list_evaluation_datasets(project_id: uuid.UUID, service: EvaluationService = Depends(get_service)):
    return success_response(
        [EvaluationDatasetRead.model_validate(d) for d in service.list_evaluation_datasets(project_id)]
    )


@router.get("/evaluation-results", response_model=ApiResponse[list[EvaluationResultRead]])
def list_evaluation_results(project_id: uuid.UUID, service: EvaluationService = Depends(get_service)):
    return success_response([EvaluationResultRead.model_validate(r) for r in service.list_evaluation_results(project_id)])


@router.post(
    "/model-versions/{model_version_id}/evaluate",
    response_model=ApiResponse[EvaluationResultRead],
    status_code=201,
)
def evaluate_model_version(
    project_id: uuid.UUID,
    model_version_id: uuid.UUID,
    payload: EvaluationRunRequest = EvaluationRunRequest(),
    service: EvaluationService = Depends(get_service),
):
    return success_response(
        EvaluationResultRead.model_validate(service.evaluate_model_version(project_id, model_version_id, payload))
    )
