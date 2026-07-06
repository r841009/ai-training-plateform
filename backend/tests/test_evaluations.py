import io
import uuid
import zipfile
from pathlib import Path

from PIL import Image

from app.db import get_db
from app.main import app as fastapi_app
from worker.worker_manager import WorkerManager


def _real_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), color="blue").save(buf, format="JPEG")
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
    return dataset["id"]


def _create_model_version(client, project_id: str, dataset_version_id: str) -> dict:
    base_model_id, trainer_id = _catalog_ids(client)
    server = client.post("/training-servers", json={"hostname": f"eval-{project_id[:8]}"}).json()["data"]
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
    job = client.post(
        f"/projects/{project_id}/training-jobs",
        json={
            "dataset_version_id": dataset_version_id,
            "base_model_id": base_model_id,
            "trainer_id": trainer_id,
            "resource_requirement_json": {"required_gpu_memory_gb": 8},
            "training_config_json": {"epochs": 1},
        },
    ).json()["data"]
    dispatch = client.post("/scheduler/dispatch-once")
    assert dispatch.json()["data"]["dispatched"] == 1

    override_get_db = fastapi_app.dependency_overrides[get_db]
    db_gen = override_get_db()
    db = next(db_gen)
    try:
        WorkerManager(db, uuid.UUID(server["id"])).run_once(limit=1)
    finally:
        db_gen.close()

    return client.get(f"/projects/{project_id}/model-versions").json()["data"][0]


def test_create_evaluation_dataset_and_mock_evaluate_model_version(client):
    project_id = _create_project(client, "EVAL_OK")
    dataset_version_id = _create_ready_dataset(client, project_id)
    model_version = _create_model_version(client, project_id, dataset_version_id)

    evaluation_dataset = client.post(
        f"/projects/{project_id}/evaluation-datasets",
        json={"name": "holdout", "dataset_version_id": dataset_version_id},
    )
    assert evaluation_dataset.status_code == 201
    evaluation_dataset_id = evaluation_dataset.json()["data"]["id"]

    resp = client.post(
        f"/projects/{project_id}/model-versions/{model_version['id']}/evaluate",
        json={"evaluation_dataset_id": evaluation_dataset_id},
    )

    assert resp.status_code == 201
    result = resp.json()["data"]
    assert result["model_version_id"] == model_version["id"]
    assert result["evaluation_dataset_id"] == evaluation_dataset_id
    assert result["metrics_json"]["f1"] == 0.87
    assert Path(result["report_path"]).exists()
    assert Path(result["sample_predictions_path"]).exists()
    listed = client.get(f"/projects/{project_id}/evaluation-results").json()["data"]
    assert [r["id"] for r in listed] == [result["id"]]


def test_evaluation_dataset_is_project_scoped(client):
    p1 = _create_project(client, "EVAL_A")
    p2 = _create_project(client, "EVAL_B")
    dataset_version_id = _create_ready_dataset(client, p1)
    model_version = _create_model_version(client, p1, dataset_version_id)
    external = client.post(
        f"/projects/{p2}/evaluation-datasets",
        json={"name": "external", "storage_path": "external/eval"},
    ).json()["data"]

    resp = client.post(
        f"/projects/{p1}/model-versions/{model_version['id']}/evaluate",
        json={"evaluation_dataset_id": external["id"]},
    )

    assert resp.status_code == 404
