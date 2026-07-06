import io
import uuid
import zipfile
import json
from pathlib import Path

from PIL import Image

from app.config import get_settings
from app.db import get_db
from app.main import app as fastapi_app
from app.models.checkpoint import Checkpoint
from worker.worker_manager import WorkerManager


def _real_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), color="purple").save(buf, format="JPEG")
    return buf.getvalue()


def _make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _create_project(client, code: str) -> str:
    resp = client.post("/projects", json={"project_code": code, "name": code})
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


def _catalog_ids(client) -> tuple[str, str]:
    base_models = client.get("/base-models").json()["data"]
    trainers = client.get("/trainers").json()["data"]
    base_model = next(m for m in base_models if m["name"] == "fasterrcnn_resnet50_fpn")
    trainer = next(t for t in trainers if t["base_model_family"] == base_model["family"])
    return base_model["id"], trainer["id"]


def _create_ready_dataset(client, project_id: str) -> str:
    dataset = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]
    zip_bytes = _make_zip(
        {
            "images/img_0.jpg": _real_jpeg_bytes(),
            "labels/img_0.txt": b"0 0.5 0.5 0.2 0.2\n",
        }
    )
    upload = client.post(
        f"/projects/{project_id}/datasets/{dataset['id']}/upload",
        files={"file": ("dataset.zip", zip_bytes, "application/zip")},
    )
    assert upload.status_code == 200
    process = client.post(f"/projects/{project_id}/datasets/{dataset['id']}/process", json={})
    assert process.status_code == 200
    assert process.json()["data"]["status"] == "READY"
    return dataset["id"]


def _create_training_server(client, hostname: str) -> str:
    server = client.post(
        "/training-servers",
        json={"hostname": hostname, "ip_address": "10.0.0.31", "max_concurrent_jobs": 1},
    ).json()["data"]
    heartbeat = client.post(
        f"/training-servers/{server['id']}/heartbeat",
        json={
            "status": "ONLINE",
            "gpu_count": 1,
            "gpu_memory_total_gb": 24,
            "gpu_memory_free_gb": 16,
            "gpu_utilization_percent": 10,
            "cpu_usage_percent": 20,
            "ram_total_gb": 128,
            "ram_free_gb": 64,
            "disk_free_gb": 256,
            "running_job_count": 0,
            "max_concurrent_jobs": 1,
        },
    )
    assert heartbeat.status_code == 200
    return server["id"]


def _create_dispatched_job(client, project_id: str, dataset_version_id: str, training_config: dict) -> tuple[str, str]:
    base_model_id, trainer_id = _catalog_ids(client)
    server_id = _create_training_server(client, f"worker-server-{project_id[:8]}")
    create_job = client.post(
        f"/projects/{project_id}/training-jobs",
        json={
            "dataset_version_id": dataset_version_id,
            "base_model_id": base_model_id,
            "trainer_id": trainer_id,
            "resource_requirement_json": {
                "required_gpu_memory_gb": 8,
                "required_ram_gb": 16,
                "required_disk_gb": 50,
                "preferred_gpu_count": 1,
            },
            "training_config_json": training_config,
        },
    )
    assert create_job.status_code == 201
    job_id = create_job.json()["data"]["id"]

    dispatch = client.post("/scheduler/dispatch-once")
    assert dispatch.status_code == 200
    assert dispatch.json()["data"]["dispatched"] == 1
    return server_id, job_id


def _create_training_job(client, project_id: str, dataset_version_id: str, training_config: dict) -> str:
    base_model_id, trainer_id = _catalog_ids(client)
    create_job = client.post(
        f"/projects/{project_id}/training-jobs",
        json={
            "dataset_version_id": dataset_version_id,
            "base_model_id": base_model_id,
            "trainer_id": trainer_id,
            "resource_requirement_json": {
                "required_gpu_memory_gb": 8,
                "required_ram_gb": 16,
                "required_disk_gb": 50,
                "preferred_gpu_count": 1,
            },
            "training_config_json": training_config,
        },
    )
    assert create_job.status_code == 201
    return create_job.json()["data"]["id"]


def _run_worker_once(server_id: str, runner=None):
    override_get_db = fastapi_app.dependency_overrides[get_db]
    db_gen = override_get_db()
    db = next(db_gen)
    try:
        return WorkerManager(db, uuid.UUID(server_id), runner=runner).run_once(limit=1)
    finally:
        db_gen.close()


def test_worker_manager_completes_dispatched_job_and_captures_log(client):
    project_id = _create_project(client, "WORKER_OK")
    dataset_version_id = _create_ready_dataset(client, project_id)
    server_id, job_id = _create_dispatched_job(client, project_id, dataset_version_id, {"epochs": 2})

    summary = _run_worker_once(server_id)

    assert summary.scanned == 1
    assert summary.succeeded == 1
    assert summary.failed == 0
    assert summary.results[0].training_job_id == uuid.UUID(job_id)
    assert summary.results[0].status == "SUCCESS"
    assert summary.results[0].log_path is not None
    assert Path(summary.results[0].log_path).read_text().endswith("mock trainer finished successfully\n")

    job = client.get(f"/projects/{project_id}/training-jobs/{job_id}").json()["data"]
    assert job["status"] == "SUCCESS"
    assert job["failure_reason"] is None
    assert client.get(f"/training-servers/{server_id}").json()["data"]["running_job_count"] == 0

    model_versions = client.get(f"/projects/{project_id}/model-versions").json()["data"]
    assert len(model_versions) == 1
    assert model_versions[0]["training_job_id"] == job_id
    assert model_versions[0]["version_no"] == 1
    assert model_versions[0]["name"].startswith("WORKER_OK_fasterrcnn_resnet50_fpn_")
    assert Path(model_versions[0]["artifact_path"]).exists()
    model_version = client.get(f"/projects/{project_id}/model-versions/{model_versions[0]['id']}").json()["data"]
    assert model_version["id"] == model_versions[0]["id"]


def test_worker_manager_marks_failed_when_mock_trainer_fails(client):
    project_id = _create_project(client, "WORKER_FAIL")
    dataset_version_id = _create_ready_dataset(client, project_id)
    server_id, job_id = _create_dispatched_job(
        client,
        project_id,
        dataset_version_id,
        {"epochs": 1, "mock_success": False, "mock_failure_reason": "forced failure"},
    )

    summary = _run_worker_once(server_id)

    assert summary.scanned == 1
    assert summary.succeeded == 0
    assert summary.failed == 1
    assert summary.results[0].status == "FAILED"
    assert summary.results[0].failure_reason == "forced failure"
    assert "forced failure" in Path(summary.results[0].log_path).read_text()

    job = client.get(f"/projects/{project_id}/training-jobs/{job_id}").json()["data"]
    assert job["status"] == "FAILED"
    assert job["failure_reason"] == "forced failure"
    assert client.get(f"/training-servers/{server_id}").json()["data"]["running_job_count"] == 0


def test_worker_manager_marks_interrupted_job_resumable_when_latest_checkpoint_exists(client):
    project_code = "WORKER_INTR"
    project_id = _create_project(client, project_code)
    dataset_version_id = _create_ready_dataset(client, project_id)
    server_id, job_id = _create_dispatched_job(client, project_id, dataset_version_id, {"epochs": 2})

    class InterruptingRunner:
        def run(self, job, resume=False):
            job_dir = Path(get_settings().storage_root) / "projects" / project_code / "training-jobs" / str(job.id)
            job_dir.mkdir(parents=True, exist_ok=True)
            (job_dir / "checkpoint_latest.pt").write_text(json.dumps({"epoch": 1, "val_loss": 0.5}))
            raise KeyboardInterrupt()

    summary = _run_worker_once(server_id, runner=InterruptingRunner())

    assert summary.results[0].status == "RESUMABLE"
    job = client.get(f"/projects/{project_id}/training-jobs/{job_id}").json()["data"]
    assert job["status"] == "RESUMABLE"
    assert client.get(f"/training-servers/{server_id}").json()["data"]["running_job_count"] == 0

    override_get_db = fastapi_app.dependency_overrides[get_db]
    db_gen = override_get_db()
    db = next(db_gen)
    try:
        checkpoint = db.query(Checkpoint).filter(Checkpoint.training_job_id == uuid.UUID(job_id)).one()
        assert checkpoint.epoch == 1
        assert checkpoint.is_latest is True
    finally:
        db_gen.close()


def test_resume_api_scheduler_and_worker_continue_from_latest_checkpoint(client):
    project_code = "WORKER_RESUME"
    project_id = _create_project(client, project_code)
    dataset_version_id = _create_ready_dataset(client, project_id)
    job_id = _create_training_job(client, project_id, dataset_version_id, {"epochs": 2})
    job_dir = Path(get_settings().storage_root) / "projects" / project_code / "training-jobs" / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    (job_dir / "checkpoint_latest.pt").write_text(json.dumps({"epoch": 1}))

    override_get_db = fastapi_app.dependency_overrides[get_db]
    db_gen = override_get_db()
    db = next(db_gen)
    try:
        from app.models.training_job import TrainingJob

        job = db.get(TrainingJob, uuid.UUID(job_id))
        job.status = "INTERRUPTED"
        db.commit()
    finally:
        db_gen.close()

    resume = client.post(f"/projects/{project_id}/training-jobs/{job_id}/resume")
    assert resume.status_code == 200
    assert resume.json()["data"]["status"] == "RESUMABLE"
    assert resume.json()["data"]["training_config_json"]["resume"] is True

    server_id = _create_training_server(client, "worker-resume-server")
    dispatch = client.post("/scheduler/dispatch-once")
    assert dispatch.status_code == 200
    assert dispatch.json()["data"]["dispatched"] == 1

    summary = _run_worker_once(server_id)

    assert summary.results[0].status == "SUCCESS"
    log_text = Path(summary.results[0].log_path).read_text()
    assert "resume=true" in log_text
    assert "epoch=1/2 status=completed" not in log_text
    assert "epoch=2/2 status=completed" in log_text


def test_retrain_creates_child_training_job_and_model_version(client):
    project_id = _create_project(client, "WORKER_RETRAIN")
    dataset_version_id = _create_ready_dataset(client, project_id)
    server_id, _ = _create_dispatched_job(client, project_id, dataset_version_id, {"epochs": 1})
    _run_worker_once(server_id)
    parent_model = client.get(f"/projects/{project_id}/model-versions").json()["data"][0]

    retrain = client.post(f"/projects/{project_id}/model-versions/{parent_model['id']}/retrain")

    assert retrain.status_code == 201
    child_job = retrain.json()["data"]
    assert child_job["status"] == "PENDING"
    assert child_job["dataset_version_id"] == dataset_version_id
    assert child_job["training_config_json"]["parent_model_version_id"] == parent_model["id"]
    assert "resume" not in child_job["training_config_json"]

    child_server_id = _create_training_server(client, "worker-retrain-server")
    dispatch = client.post("/scheduler/dispatch-once")
    assert dispatch.status_code == 200
    assert dispatch.json()["data"]["dispatched"] == 1
    _run_worker_once(child_server_id)

    model_versions = client.get(f"/projects/{project_id}/model-versions").json()["data"]
    child_model = next(m for m in model_versions if m["training_job_id"] == child_job["id"])
    assert child_model["version_no"] == 2
    assert child_model["parent_model_version_id"] == parent_model["id"]


def test_retrain_is_project_scoped(client):
    p1 = _create_project(client, "WORKER_RETRAIN_A")
    p2 = _create_project(client, "WORKER_RETRAIN_B")
    dataset_version_id = _create_ready_dataset(client, p1)
    server_id, _ = _create_dispatched_job(client, p1, dataset_version_id, {"epochs": 1})
    _run_worker_once(server_id)
    parent_model = client.get(f"/projects/{p1}/model-versions").json()["data"][0]

    resp = client.post(f"/projects/{p2}/model-versions/{parent_model['id']}/retrain")

    assert resp.status_code == 404
