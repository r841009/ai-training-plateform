import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session):
        self.repo = ProjectRepository(db)

    def create_project(self, payload: ProjectCreate) -> Project:
        if self.repo.get_by_code(payload.project_code):
            raise HTTPException(
                status.HTTP_409_CONFLICT, f"project_code '{payload.project_code}' already exists"
            )
        project = Project(
            project_code=payload.project_code, name=payload.name, description=payload.description
        )
        return self.repo.create(project)

    def get_project(self, project_id: uuid.UUID) -> Project:
        project = self.repo.get(project_id)
        if project is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
        return project

    def list_projects(self) -> list[Project]:
        return self.repo.list()

    def update_project(self, project_id: uuid.UUID, payload: ProjectUpdate) -> Project:
        project = self.get_project(project_id)
        if payload.name is not None:
            project.name = payload.name
        if payload.description is not None:
            project.description = payload.description
        return self.repo.save(project)

    def delete_project(self, project_id: uuid.UUID) -> None:
        project = self.get_project(project_id)
        self.repo.delete(project)
