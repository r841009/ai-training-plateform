import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.response import ApiResponse, success_response
from app.schemas.training_server import (
    TrainingServerCreate,
    TrainingServerHeartbeat,
    TrainingServerRead,
)
from app.services.training_server_service import TrainingServerService

router = APIRouter(prefix="/training-servers", tags=["training-servers"])


def get_service(db: Session = Depends(get_db)) -> TrainingServerService:
    return TrainingServerService(db)


@router.post("", response_model=ApiResponse[TrainingServerRead], status_code=201)
def create_training_server(
    payload: TrainingServerCreate, service: TrainingServerService = Depends(get_service)
):
    return success_response(TrainingServerRead.model_validate(service.create_training_server(payload)))


@router.get("", response_model=ApiResponse[list[TrainingServerRead]])
def list_training_servers(service: TrainingServerService = Depends(get_service)):
    return success_response([TrainingServerRead.model_validate(s) for s in service.list_training_servers()])


@router.get("/{training_server_id}", response_model=ApiResponse[TrainingServerRead])
def get_training_server(
    training_server_id: uuid.UUID, service: TrainingServerService = Depends(get_service)
):
    return success_response(TrainingServerRead.model_validate(service.get_training_server(training_server_id)))


@router.post("/{training_server_id}/heartbeat", response_model=ApiResponse[TrainingServerRead])
def record_training_server_heartbeat(
    training_server_id: uuid.UUID,
    payload: TrainingServerHeartbeat,
    service: TrainingServerService = Depends(get_service),
):
    return success_response(
        TrainingServerRead.model_validate(service.record_heartbeat(training_server_id, payload))
    )
