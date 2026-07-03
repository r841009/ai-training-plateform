from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.dataset_version import DatasetVersion
from app.models.training_job import TrainingJob
from app.models.training_server import TrainingServer
from app.repositories.dataset_version_repository import DatasetVersionRepository
from app.repositories.training_job_repository import TrainingJobRepository
from app.repositories.training_server_repository import TrainingServerRepository
from app.schemas.scheduler import DispatchDecision, DispatchSummary


@dataclass(frozen=True)
class ResourceRequirement:
    required_gpu_memory_gb: float = 0.0
    required_ram_gb: float = 0.0
    required_disk_gb: float = 0.0
    preferred_gpu_count: int = 0


class SchedulerService:
    def __init__(self, db: Session):
        self.job_repo = TrainingJobRepository(db)
        self.dataset_repo = DatasetVersionRepository(db)
        self.server_repo = TrainingServerRepository(db)

    def dispatch_once(self) -> DispatchSummary:
        jobs = self.job_repo.list_dispatch_candidates()
        decisions: list[DispatchDecision] = []
        dispatched = 0
        queued = 0
        failed = 0

        for job in jobs:
            dataset = self.dataset_repo.get_for_project(job.project_id, job.dataset_version_id)
            if not self._dataset_ready(dataset):
                job.status = "FAILED"
                job.failure_reason = "dataset version is not READY"
                self.job_repo.save(job)
                failed += 1
                decisions.append(
                    DispatchDecision(
                        training_job_id=job.id,
                        status=job.status,
                        reason=job.failure_reason,
                    )
                )
                continue

            server = self._find_server_for_job(job, self.server_repo.list_online())
            if server is None:
                job.status = "QUEUED"
                job.assigned_server_id = None
                self.job_repo.save(job)
                queued += 1
                decisions.append(
                    DispatchDecision(
                        training_job_id=job.id,
                        status=job.status,
                        reason="no training server has enough free resources",
                    )
                )
                continue

            job.status = "DISPATCHED"
            job.assigned_server_id = server.id
            job.failure_reason = None
            server.running_job_count += 1
            self.server_repo.save(server)
            self.job_repo.save(job)
            dispatched += 1
            decisions.append(
                DispatchDecision(training_job_id=job.id, status=job.status, assigned_server_id=server.id)
            )

        return DispatchSummary(
            scanned=len(jobs),
            dispatched=dispatched,
            queued=queued,
            failed=failed,
            decisions=decisions,
        )

    def _find_server_for_job(
        self, job: TrainingJob, servers: list[TrainingServer]
    ) -> TrainingServer | None:
        requirement = self._parse_requirement(job.resource_requirement_json)
        for server in servers:
            if self._server_can_run(server, requirement):
                return server
        return None

    @staticmethod
    def _dataset_ready(dataset: DatasetVersion | None) -> bool:
        return dataset is not None and dataset.status == "READY"

    @staticmethod
    def _parse_requirement(payload: dict) -> ResourceRequirement:
        return ResourceRequirement(
            required_gpu_memory_gb=float(payload.get("required_gpu_memory_gb", 0) or 0),
            required_ram_gb=float(payload.get("required_ram_gb", 0) or 0),
            required_disk_gb=float(payload.get("required_disk_gb", 0) or 0),
            preferred_gpu_count=int(payload.get("preferred_gpu_count", 0) or 0),
        )

    @staticmethod
    def _server_can_run(server: TrainingServer, requirement: ResourceRequirement) -> bool:
        return (
            server.gpu_count >= requirement.preferred_gpu_count
            and server.gpu_memory_free_gb >= requirement.required_gpu_memory_gb
            and server.ram_free_gb >= requirement.required_ram_gb
            and server.disk_free_gb >= requirement.required_disk_gb
            and server.running_job_count < server.max_concurrent_jobs
        )

