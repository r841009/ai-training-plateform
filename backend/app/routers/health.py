import logging

from fastapi import APIRouter

from app.db import ping_db
from app.schemas.response import ApiResponse, success_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health", response_model=ApiResponse[dict])
def health() -> ApiResponse[dict]:
    try:
        ping_db()
        db_status = "ok"
    except Exception:
        logger.exception("database health check failed")
        db_status = "unavailable"

    return success_response({"status": "ok", "database": db_status})
