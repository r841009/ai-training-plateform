from __future__ import annotations

import traceback
import uuid
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import SessionLocal
from app.models.checkpoint import Checkpoint
from app.models.training_job import TrainingJob
from app.repositories.checkpoint_repository import CheckpointRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.training_job_repository import TrainingJobRepository
from app.repositories.training_server_repository import TrainingServerRepository
from app.services.model_version_service import ModelVersionService


@dataclass(frozen=True)
class TrainerRunResult:
    success: bool
    log_text: str
    failure_reason: str | None = None


class MockTrainerRunner:
    def run(self, job: TrainingJob, resume: bool = False) -> TrainerRunResult:
        config = job.training_config_json or {}
        epochs = int(config.get("epochs", 1) or 1)
        requested_success = bool(config.get("mock_success", True))
        failure_reason = str(config.get("mock_failure_reason", "mock trainer failed"))
        start_epoch = 1
        checkpoint_path = config.get("checkpoint_latest_path")
        if resume and checkpoint_path and Path(checkpoint_path).exists():
            start_epoch = int(json.loads(Path(checkpoint_path).read_text()).get("epoch", 0)) + 1

        lines = [
            f"job_id={job.id}",
            f"project_id={job.project_id}",
            f"dataset_version_id={job.dataset_version_id}",
            f"epochs={epochs}",
            f"resume={str(resume).lower()}",
            "mock trainer started",
        ]
        for epoch in range(start_epoch, epochs + 1):
            lines.append(f"epoch={epoch}/{epochs} status=completed")

        if requested_success:
            lines.append("mock trainer finished successfully")
            return TrainerRunResult(success=True, log_text="\n".join(lines) + "\n")

        lines.append(f"mock trainer failed: {failure_reason}")
        return TrainerRunResult(success=False, log_text="\n".join(lines) + "\n", failure_reason=failure_reason)


@dataclass(frozen=True)
class WorkerJobResult:
    training_job_id: uuid.UUID
    status: str
    log_path: str | None = None
    failure_reason: str | None = None


@dataclass(frozen=True)
class WorkerRunSummary:
    scanned: int
    succeeded: int
    failed: int
    skipped: int
    results: list[WorkerJobResult] = field(default_factory=list)


class WorkerManager:
    def __init__(self, db: Session, server_id: uuid.UUID, runner: MockTrainerRunner | None = None):
        self.db = db
        self.server_id = server_id
        self.runner = runner or MockTrainerRunner()
        self.job_repo = TrainingJobRepository(db)
        self.checkpoint_repo = CheckpointRepository(db)
        self.server_repo = TrainingServerRepository(db)
        self.project_repo = ProjectRepository(db)

    def run_once(self, limit: int = 1) -> WorkerRunSummary:
        server = self.server_repo.get(self.server_id)
        if server is None:
            return WorkerRunSummary(
                scanned=0,
                succeeded=0,
                failed=0,
                skipped=1,
                results=[],
            )

        self._heartbeat()
        jobs = self.job_repo.list_dispatched_for_server(self.server_id, limit=limit)
        results = [self._run_job(job) for job in jobs]

        return WorkerRunSummary(
            scanned=len(jobs),
            succeeded=sum(result.status == "SUCCESS" for result in results),
            failed=sum(result.status == "FAILED" for result in results),
            skipped=0,
            results=results,
        )

    def _run_job(self, job: TrainingJob) -> WorkerJobResult:
        resume = bool((job.training_config_json or {}).get("resume"))
        if resume:
            job.training_config_json = {
                **(job.training_config_json or {}),
                "checkpoint_latest_path": str(self._latest_checkpoint_path(job)),
            }
        job.status = "RUNNING"
        job.failure_reason = None
        self.job_repo.save(job)
        self._heartbeat()

        try:
            trainer_result = self.runner.run(job, resume=resume)
        except KeyboardInterrupt:
            log_text = traceback.format_exc()
            log_path = self._write_log(job, log_text)
            job.status = "INTERRUPTED"
            job.failure_reason = "worker interrupted"
            if self._latest_checkpoint_path(job).exists():
                self._record_latest_checkpoint(job)
                job.status = "RESUMABLE"
                job.failure_reason = None
            self.job_repo.save(job)
            self._release_server_slot()
            self._heartbeat()
            return WorkerJobResult(job.id, job.status, str(log_path), job.failure_reason)
        except Exception as exc:  # noqa: BLE001 - worker must persist unexpected trainer failures.
            log_text = traceback.format_exc()
            log_path = self._write_log(job, log_text)
            job.status = "FAILED"
            job.failure_reason = str(exc)
            self.job_repo.save(job)
            self._release_server_slot()
            self._heartbeat()
            return WorkerJobResult(job.id, job.status, str(log_path), job.failure_reason)

        log_path = self._write_log(job, trainer_result.log_text)
        if trainer_result.success:
            job.status = "SUCCESS"
            job.failure_reason = None
            self._write_model_artifact(job)
            ModelVersionService(self.db).create_from_training_job(job, str(self._model_artifact_path(job)))
        else:
            job.status = "FAILED"
            job.failure_reason = trainer_result.failure_reason or "trainer failed"
        self.job_repo.save(job)
        self._release_server_slot()
        self._heartbeat()
        return WorkerJobResult(job.id, job.status, str(log_path), job.failure_reason)

    def _write_log(self, job: TrainingJob, log_text: str) -> Path:
        log_dir = self._job_dir(job)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "worker.log"
        log_path.write_text(log_text)
        return log_path

    def _job_dir(self, job: TrainingJob) -> Path:
        project = self.project_repo.get(job.project_id)
        project_code = project.project_code if project is not None else str(job.project_id)
        return Path(get_settings().storage_root) / "projects" / project_code / "training-jobs" / str(job.id)

    def _latest_checkpoint_path(self, job: TrainingJob) -> Path:
        return self._job_dir(job) / "checkpoint_latest.pt"

    def _model_artifact_path(self, job: TrainingJob) -> Path:
        return self._job_dir(job) / "model_artifact.json"

    def _write_model_artifact(self, job: TrainingJob) -> None:
        path = self._model_artifact_path(job)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"training_job_id": str(job.id), "status": "SUCCESS"}, indent=2))

    def _record_latest_checkpoint(self, job: TrainingJob) -> None:
        latest_path = self._latest_checkpoint_path(job)
        try:
            payload = json.loads(latest_path.read_text())
        except json.JSONDecodeError:
            payload = {}
        self.checkpoint_repo.create(
            Checkpoint(
                project_id=job.project_id,
                training_job_id=job.id,
                checkpoint_path=str(latest_path),
                epoch=payload.get("epoch"),
                metrics_json=payload,
                is_latest=True,
                is_best=False,
            )
        )

    def _heartbeat(self) -> None:
        server = self.server_repo.get(self.server_id)
        if server is None:
            return
        server.status = "ONLINE"
        server.last_heartbeat_at = datetime.now(timezone.utc)
        self.server_repo.save(server)

    def _release_server_slot(self) -> None:
        server = self.server_repo.get(self.server_id)
        if server is None:
            return
        server.running_job_count = max(0, server.running_job_count - 1)
        self.server_repo.save(server)


def run_once(server_id: uuid.UUID, limit: int = 1) -> WorkerRunSummary:
    db = SessionLocal()
    try:
        return WorkerManager(db, server_id).run_once(limit=limit)
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m worker.worker_manager <training_server_id> [limit]")
    summary = run_once(uuid.UUID(sys.argv[1]), limit=int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    print(summary)
