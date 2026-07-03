import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.training_server import TrainingServer
from app.repositories.training_server_repository import TrainingServerRepository
from app.schemas.training_server import TrainingServerCreate, TrainingServerHeartbeat


class TrainingServerService:
    def __init__(self, db: Session):
        self.repo = TrainingServerRepository(db)

    def create_training_server(self, payload: TrainingServerCreate) -> TrainingServer:
        if self.repo.get_by_hostname(payload.hostname):
            raise HTTPException(status.HTTP_409_CONFLICT, f"hostname '{payload.hostname}' already exists")

        training_server = TrainingServer(
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            status="REGISTERED",
            max_concurrent_jobs=payload.max_concurrent_jobs,
        )
        return self.repo.create(training_server)

    def get_training_server(self, training_server_id: uuid.UUID) -> TrainingServer:
        training_server = self.repo.get(training_server_id)
        if training_server is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "training server not found")
        return training_server

    def list_training_servers(self) -> list[TrainingServer]:
        return self.repo.list()

    def record_heartbeat(
        self, training_server_id: uuid.UUID, payload: TrainingServerHeartbeat
    ) -> TrainingServer:
        training_server = self.get_training_server(training_server_id)
        training_server.status = payload.status
        training_server.gpu_count = payload.gpu_count
        training_server.gpu_memory_total_gb = payload.gpu_memory_total_gb
        training_server.gpu_memory_free_gb = payload.gpu_memory_free_gb
        training_server.gpu_utilization_percent = payload.gpu_utilization_percent
        training_server.cpu_usage_percent = payload.cpu_usage_percent
        training_server.ram_total_gb = payload.ram_total_gb
        training_server.ram_free_gb = payload.ram_free_gb
        training_server.disk_free_gb = payload.disk_free_gb
        training_server.running_job_count = payload.running_job_count
        if payload.max_concurrent_jobs is not None:
            training_server.max_concurrent_jobs = payload.max_concurrent_jobs
        training_server.last_heartbeat_at = datetime.now(timezone.utc)
        return self.repo.save(training_server)

