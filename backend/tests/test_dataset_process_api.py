import io
import zipfile
from pathlib import Path

from PIL import Image


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


def _create_project_with_uploaded_dataset(client, code: str, n_images: int = 10):
    project_id = client.post("/projects", json={"project_code": code, "name": code}).json()["data"]["id"]
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]

    files = {}
    for i in range(n_images):
        files[f"images/img_{i}.jpg"] = _real_jpeg_bytes()
        files[f"labels/img_{i}.txt"] = b"0 0.5 0.5 0.2 0.2\n"
    zip_bytes = _make_zip(files)

    client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("dataset.zip", zip_bytes, "application/zip")},
    )
    return project_id, dv["id"]


def test_process_dataset_transitions_to_ready(client):
    project_id, dv_id = _create_project_with_uploaded_dataset(client, "PROC_OK", n_images=10)

    resp = client.post(f"/projects/{project_id}/datasets/{dv_id}/process", json={})
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "READY"

    storage_path = Path(resp.json()["data"]["storage_path"])
    assert (storage_path / "manifests" / "dataset_manifest.jsonl").exists()
    assert (storage_path / "manifests" / "class_mapping.json").exists()
    assert (storage_path / "manifests" / "dataset_statistics.json").exists()
    assert (storage_path / "splits" / "train.txt").exists()
    assert (storage_path / "validation" / "validation_report.json").exists()


def test_process_dataset_with_no_valid_images_marks_invalid(client):
    project_id = client.post("/projects", json={"project_code": "PROC_BAD", "name": "x"}).json()["data"]["id"]
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]

    zip_bytes = _make_zip({"images/a.jpg": b"not a real image", "labels/a.txt": b"0 0.5 0.5 0.2 0.2\n"})
    client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("dataset.zip", zip_bytes, "application/zip")},
    )

    resp = client.post(f"/projects/{project_id}/datasets/{dv['id']}/process", json={})
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "INVALID"


def test_process_rejects_ratios_not_summing_to_one(client):
    project_id, dv_id = _create_project_with_uploaded_dataset(client, "PROC_RATIO", n_images=3)
    resp = client.post(
        f"/projects/{project_id}/datasets/{dv_id}/process",
        json={"train_ratio": 0.5, "val_ratio": 0.5, "test_ratio": 0.5},
    )
    assert resp.status_code == 422


def test_process_blocked_when_not_uploaded(client):
    project_id = client.post("/projects", json={"project_code": "PROC_EARLY", "name": "x"}).json()["data"]["id"]
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]  # status = CREATED, no upload yet

    resp = client.post(f"/projects/{project_id}/datasets/{dv['id']}/process", json={})
    assert resp.status_code == 409


def test_process_twice_blocked_second_time(client):
    project_id, dv_id = _create_project_with_uploaded_dataset(client, "PROC_TWICE", n_images=3)
    first = client.post(f"/projects/{project_id}/datasets/{dv_id}/process", json={})
    assert first.json()["data"]["status"] == "READY"

    second = client.post(f"/projects/{project_id}/datasets/{dv_id}/process", json={})
    assert second.status_code == 409
