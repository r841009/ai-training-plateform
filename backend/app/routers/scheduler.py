from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.response import ApiResponse, success_response
from app.schemas.scheduler import DispatchSummary
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


def get_service(db: Session = Depends(get_db)) -> SchedulerService:
    return SchedulerService(db)


@router.post("/dispatch-once", response_model=ApiResponse[DispatchSummary])
def dispatch_once(service: SchedulerService = Depends(get_service)):
    summary = service.dispatch_once()
    return success_response(summary)

