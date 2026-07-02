import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.base_model import BaseModelRead
from app.schemas.response import ApiResponse, success_response
from app.services.base_model_service import BaseModelService

router = APIRouter(prefix="/base-models", tags=["base-models"])


def get_service(db: Session = Depends(get_db)) -> BaseModelService:
    return BaseModelService(db)


@router.get("", response_model=ApiResponse[list[BaseModelRead]])
def list_base_models(service: BaseModelService = Depends(get_service)):
    base_models = service.list_base_models()
    return success_response([BaseModelRead.model_validate(m) for m in base_models])


@router.get("/{base_model_id}", response_model=ApiResponse[BaseModelRead])
def get_base_model(base_model_id: uuid.UUID, service: BaseModelService = Depends(get_service)):
    base_model = service.get_base_model(base_model_id)
    return success_response(BaseModelRead.model_validate(base_model))
