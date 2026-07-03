import io
import zipfile

from PIL import Image


def _real_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), color="yellow").save(buf, format="JPEG")
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
    return base_models[0]["id"], trainers[0]["id"]


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


def _create_uploaded_dataset(client, project_id: str) -> str:
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
    return dataset["id"]


def _create_training_server(
    client,
    hostname: str,
    gpu_memory_free_gb: float = 16,
    ram_free_gb: float = 64,
    disk_free_gb: float = 256,
    max_concurrent_jobs: int = 1,
) -> str:
    server = client.post(
        "/training-servers",
        json={"hostname": hostname, "ip_address": "10.0.0.21", "max_concurrent_jobs": max_concurrent_jobs},
    ).json()["data"]
    heartbeat = client.post(
        f"/training-servers/{server['id']}/heartbeat",
        json={
            "status": "ONLINE",
            "gpu_count": 1,
            "gpu_memory_total_gb": 24,
            "gpu_memory_free_gb": gpu_memory_free_gb,
            "gpu_utilization_percent": 10,
            "cpu_usage_percent": 20,
            "ram_total_gb": 128,
            "ram_free_gb": ram_free_gb,
            "disk_free_gb": disk_free_gb,
            "running_job_count": 0,
            "max_concurrent_jobs": max_concurrent_jobs,
        },
    )
    assert heartbeat.status_code == 200
    return server["id"]


def _create_training_job(
    client,
    project_id: str,
    dataset_version_id: str,
    required_gpu_memory_gb: float = 8,
    required_ram_gb: float = 16,
    required_disk_gb: float = 50,
) -> dict:
    base_model_id, trainer_id = _catalog_ids(client)
    resp = client.post(
        f"/projects/{project_id}/training-jobs",
        json={
            "dataset_version_id": dataset_version_id,
            "base_model_id": base_model_id,
            "trainer_id": trainer_id,
            "resource_requirement_json": {
                "required_gpu_memory_gb": required_gpu_memory_gb,
                "required_ram_gb": required_ram_gb,
                "required_disk_gb": required_disk_gb,
                "preferred_gpu_count": 1,
            },
            "training_config_json": {"epochs": 1},
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]


def test_dispatch_once_assigns_job_when_resources_are_available(client):
    project_id = _create_project(client, "SCHED_OK")
    dataset_version_id = _create_ready_dataset(client, project_id)
    server_id = _create_training_server(client, "sched-server-ok")
    job = _create_training_job(client, project_id, dataset_version_id)

    resp = client.post("/scheduler/dispatch-once")
    assert resp.status_code == 200
    summary = resp.json()["data"]
    assert summary["scanned"] == 1
    assert summary["dispatched"] == 1
    assert summary["queued"] == 0
    assert summary["failed"] == 0
    assert summary["decisions"][0]["assigned_server_id"] == server_id

    job_resp = client.get(f"/projects/{project_id}/training-jobs/{job['id']}")
    updated_job = job_resp.json()["data"]
    assert updated_job["status"] == "DISPATCHED"
    assert updated_job["assigned_server_id"] == server_id

    server_resp = client.get(f"/training-servers/{server_id}")
    assert server_resp.json()["data"]["running_job_count"] == 1


def test_dispatch_once_queues_job_when_resources_are_insufficient(client):
    project_id = _create_project(client, "SCHED_QUEUE")
    dataset_version_id = _create_ready_dataset(client, project_id)
    _create_training_server(client, "sched-server-small", gpu_memory_free_gb=4)
    job = _create_training_job(client, project_id, dataset_version_id, required_gpu_memory_gb=8)

    resp = client.post("/scheduler/dispatch-once")
    assert resp.status_code == 200
    summary = resp.json()["data"]
    assert summary["dispatched"] == 0
    assert summary["queued"] == 1
    assert summary["failed"] == 0

    job_resp = client.get(f"/projects/{project_id}/training-jobs/{job['id']}")
    updated_job = job_resp.json()["data"]
    assert updated_job["status"] == "QUEUED"
    assert updated_job["assigned_server_id"] is None


def test_dispatch_once_fails_job_when_dataset_is_no_longer_ready(client):
    project_id = _create_project(client, "SCHED_BAD_DS")
    dataset_version_id = _create_uploaded_dataset(client, project_id)
    base_model_id, trainer_id = _catalog_ids(client)
    # Bypass the create API's READY guard so Phase 8 can verify stale jobs defensively.
    from app.models.training_job import TrainingJob
    from app.db import get_db
    from app.main import app

    override = app.dependency_overrides[get_db]
    db = next(override())
    job = TrainingJob(
        project_id=project_id,
        dataset_version_id=dataset_version_id,
        base_model_id=base_model_id,
        trainer_id=trainer_id,
        status="PENDING",
        resource_requirement_json={"required_gpu_memory_gb": 1},
        training_config_json={},
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job_id = str(job.id)

    _create_training_server(client, "sched-server-ds")

    resp = client.post("/scheduler/dispatch-once")
    assert resp.status_code == 200
    summary = resp.json()["data"]
    assert summary["failed"] == 1
    assert summary["decisions"][0]["reason"] == "dataset version is not READY"

    job_resp = client.get(f"/projects/{project_id}/training-jobs/{job_id}")
    updated_job = job_resp.json()["data"]
    assert updated_job["status"] == "FAILED"
    assert updated_job["failure_reason"] == "dataset version is not READY"


def test_dispatch_once_respects_server_concurrency_limit(client):
    project_id = _create_project(client, "SCHED_LIMIT")
    dataset_version_id = _create_ready_dataset(client, project_id)
    server_id = _create_training_server(client, "sched-server-limit", max_concurrent_jobs=1)
    first = _create_training_job(client, project_id, dataset_version_id)
    second = _create_training_job(client, project_id, dataset_version_id)

    resp = client.post("/scheduler/dispatch-once")
    assert resp.status_code == 200
    summary = resp.json()["data"]
    assert summary["scanned"] == 2
    assert summary["dispatched"] == 1
    assert summary["queued"] == 1

    first_status = client.get(f"/projects/{project_id}/training-jobs/{first['id']}").json()["data"]["status"]
    second_status = client.get(f"/projects/{project_id}/training-jobs/{second['id']}").json()["data"]["status"]
    assert sorted([first_status, second_status]) == ["DISPATCHED", "QUEUED"]
    assert client.get(f"/training-servers/{server_id}").json()["data"]["running_job_count"] == 1

