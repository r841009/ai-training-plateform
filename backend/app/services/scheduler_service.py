from sqlalchemy.orm import Session

from app.models.training_job import TrainingJob
from app.models.training_server import TrainingServer
from app.repositories.dataset_version_repository import DatasetVersionRepository
from app.repositories.training_job_repository import TrainingJobRepository
from app.repositories.training_server_repository import TrainingServerRepository
from app.schemas.scheduler import DispatchDecision, DispatchSummary


class SchedulerService:
    def __init__(self, db: Session):
        self.job_repo = TrainingJobRepository(db)
        self.dataset_repo = DatasetVersionRepository(db)
        self.server_repo = TrainingServerRepository(db)

    def dispatch_once(self) -> DispatchSummary:
        jobs = self.job_repo.list_dispatch_candidates()
        decisions: list[DispatchDecision] = []

        for job in jobs:
            dataset = self.dataset_repo.get_for_project(job.project_id, job.dataset_version_id)
            if dataset is None or dataset.status != "READY":
                job.status = "FAILED"
                job.failure_reason = "dataset version is not READY"
                self.job_repo.save(job)
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
            decisions.append(
                DispatchDecision(training_job_id=job.id, status=job.status, assigned_server_id=server.id)
            )

        return DispatchSummary(
            scanned=len(jobs),
            dispatched=sum(decision.status == "DISPATCHED" for decision in decisions),
            queued=sum(decision.status == "QUEUED" for decision in decisions),
            failed=sum(decision.status == "FAILED" for decision in decisions),
            decisions=decisions,
        )

    def _find_server_for_job(
        self, job: TrainingJob, servers: list[TrainingServer]
    ) -> TrainingServer | None:
        return next((server for server in servers if self._server_can_run(server, job.resource_requirement_json)), None)

    @staticmethod
    def _server_can_run(server: TrainingServer, requirement: dict) -> bool:
        return (
            server.gpu_count >= int(requirement.get("preferred_gpu_count", 0) or 0)
            and server.gpu_memory_free_gb >= float(requirement.get("required_gpu_memory_gb", 0) or 0)
            and server.ram_free_gb >= float(requirement.get("required_ram_gb", 0) or 0)
            and server.disk_free_gb >= float(requirement.get("required_disk_gb", 0) or 0)
            and server.running_job_count < server.max_concurrent_jobs
        )
