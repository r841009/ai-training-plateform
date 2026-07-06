import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.schemas.response import ApiResponse, success_response
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


@router.post("", response_model=ApiResponse[ProjectRead], status_code=201)
def create_project(payload: ProjectCreate, service: ProjectService = Depends(get_service)):
    return success_response(ProjectRead.model_validate(service.create_project(payload)))


@router.get("", response_model=ApiResponse[list[ProjectRead]])
def list_projects(service: ProjectService = Depends(get_service)):
    return success_response([ProjectRead.model_validate(p) for p in service.list_projects()])


@router.get("/{project_id}", response_model=ApiResponse[ProjectRead])
def get_project(project_id: uuid.UUID, service: ProjectService = Depends(get_service)):
    return success_response(ProjectRead.model_validate(service.get_project(project_id)))


@router.patch("/{project_id}", response_model=ApiResponse[ProjectRead])
def update_project(
    project_id: uuid.UUID, payload: ProjectUpdate, service: ProjectService = Depends(get_service)
):
    return success_response(ProjectRead.model_validate(service.update_project(project_id, payload)))


@router.delete("/{project_id}", response_model=ApiResponse[None])
def delete_project(project_id: uuid.UUID, service: ProjectService = Depends(get_service)):
    service.delete_project(project_id)
    return success_response(None)
