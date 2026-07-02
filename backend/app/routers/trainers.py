import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.response import ApiResponse, success_response
from app.schemas.trainer import TrainerRead
from app.services.trainer_service import TrainerService

router = APIRouter(prefix="/trainers", tags=["trainers"])


def get_service(db: Session = Depends(get_db)) -> TrainerService:
    return TrainerService(db)


@router.get("", response_model=ApiResponse[list[TrainerRead]])
def list_trainers(service: TrainerService = Depends(get_service)):
    trainers = service.list_trainers()
    return success_response([TrainerRead.model_validate(t) for t in trainers])


@router.get("/{trainer_id}", response_model=ApiResponse[TrainerRead])
def get_trainer(trainer_id: uuid.UUID, service: TrainerService = Depends(get_service)):
    trainer = service.get_trainer(trainer_id)
    return success_response(TrainerRead.model_validate(trainer))
