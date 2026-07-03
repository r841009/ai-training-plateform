import io
import uuid
import zipfile

from PIL import Image


def _real_jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (16, 16), color="green").save(buf, format="JPEG")
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


def _yolo_catalog_ids(client) -> tuple[str, str]:
    base_models = client.get("/base-models").json()["data"]
    trainers = client.get("/trainers").json()["data"]
    base_model = next(m for m in base_models if m["name"] == "yolov8s")
    trainer = next(t for t in trainers if t["trainer_name"] == "yolo_trainer")
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


def _training_job_payload(dataset_version_id: str, base_model_id: str, trainer_id: str) -> dict:
    return {
        "dataset_version_id": dataset_version_id,
        "base_model_id": base_model_id,
        "trainer_id": trainer_id,
        "resource_requirement_json": {
            "required_gpu_memory_gb": 8,
            "required_ram_gb": 16,
            "required_disk_gb": 50,
            "preferred_gpu_count": 1,
        },
        "training_config_json": {"epochs": 10, "batch_size": 8},
    }


def test_create_and_list_training_jobs(client):
    project_id = _create_project(client, "JOB_CREATE")
    dataset_version_id = _create_ready_dataset(client, project_id)
    base_model_id, trainer_id = _catalog_ids(client)

    resp = client.post(
        f"/projects/{project_id}/training-jobs",
        json=_training_job_payload(dataset_version_id, base_model_id, trainer_id),
    )

    assert resp.status_code == 201
    job = resp.json()["data"]
    assert job["project_id"] == project_id
    assert job["dataset_version_id"] == dataset_version_id
    assert job["status"] == "PENDING"
    assert job["assigned_server_id"] is None
    assert job["resource_requirement_json"]["required_gpu_memory_gb"] == 8
    assert job["training_config_json"]["epochs"] == 10

    resp = client.get(f"/projects/{project_id}/training-jobs")
    assert resp.status_code == 200
    assert [j["id"] for j in resp.json()["data"]] == [job["id"]]


def test_get_training_job_is_project_scoped(client):
    p1 = _create_project(client, "JOB_SCOPE_A")
    p2 = _create_project(client, "JOB_SCOPE_B")
    dataset_version_id = _create_ready_dataset(client, p1)
    base_model_id, trainer_id = _catalog_ids(client)
    job = client.post(
        f"/projects/{p1}/training-jobs",
        json=_training_job_payload(dataset_version_id, base_model_id, trainer_id),
    ).json()["data"]

    assert client.get(f"/projects/{p1}/training-jobs/{job['id']}").status_code == 200
    assert client.get(f"/projects/{p2}/training-jobs/{job['id']}").status_code == 404


def test_create_training_job_requires_ready_dataset(client):
    project_id = _create_project(client, "JOB_NOT_READY")
    dataset = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]
    base_model_id, trainer_id = _catalog_ids(client)

    resp = client.post(
        f"/projects/{project_id}/training-jobs",
        json=_training_job_payload(dataset["id"], base_model_id, trainer_id),
    )

    assert resp.status_code == 409


def test_create_training_job_rejects_dataset_from_another_project(client):
    p1 = _create_project(client, "JOB_DS_A")
    p2 = _create_project(client, "JOB_DS_B")
    dataset_version_id = _create_ready_dataset(client, p1)
    base_model_id, trainer_id = _catalog_ids(client)

    resp = client.post(
        f"/projects/{p2}/training-jobs",
        json=_training_job_payload(dataset_version_id, base_model_id, trainer_id),
    )

    assert resp.status_code == 404


def test_create_training_job_requires_existing_catalog_entries(client):
    project_id = _create_project(client, "JOB_CATALOG")
    dataset_version_id = _create_ready_dataset(client, project_id)
    base_model_id, trainer_id = _catalog_ids(client)

    missing_base_model = client.post(
        f"/projects/{project_id}/training-jobs",
        json=_training_job_payload(dataset_version_id, str(uuid.uuid4()), trainer_id),
    )
    assert missing_base_model.status_code == 404

    missing_trainer = client.post(
        f"/projects/{project_id}/training-jobs",
        json=_training_job_payload(dataset_version_id, base_model_id, str(uuid.uuid4())),
    )
    assert missing_trainer.status_code == 404


def test_create_training_job_blocks_restricted_yolo_model(client):
    project_id = _create_project(client, "JOB_YOLO_BLOCK")
    dataset_version_id = _create_ready_dataset(client, project_id)
    base_model_id, trainer_id = _yolo_catalog_ids(client)

    resp = client.post(
        f"/projects/{project_id}/training-jobs",
        json=_training_job_payload(dataset_version_id, base_model_id, trainer_id),
    )

    assert resp.status_code == 409
    assert "not approved for OEM" in resp.json()["error"]["message"]


def test_create_training_job_rejects_incompatible_trainer_family(client):
    project_id = _create_project(client, "JOB_TRAINER_FAMILY")
    dataset_version_id = _create_ready_dataset(client, project_id)
    base_model_id, _ = _catalog_ids(client)
    trainers = client.get("/trainers").json()["data"]
    incompatible_trainer = next(t for t in trainers if t["trainer_name"] == "detr_trainer")

    resp = client.post(
        f"/projects/{project_id}/training-jobs",
        json=_training_job_payload(dataset_version_id, base_model_id, incompatible_trainer["id"]),
    )

    assert resp.status_code == 409
    assert "does not support base model family" in resp.json()["error"]["message"]


def test_training_job_endpoints_require_existing_project(client):
    missing_project_id = uuid.uuid4()
    base_model_id, trainer_id = _catalog_ids(client)

    create_resp = client.post(
        f"/projects/{missing_project_id}/training-jobs",
        json=_training_job_payload(str(uuid.uuid4()), base_model_id, trainer_id),
    )
    assert create_resp.status_code == 404

    list_resp = client.get(f"/projects/{missing_project_id}/training-jobs")
    assert list_resp.status_code == 404
