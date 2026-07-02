import io
import uuid
import zipfile
from pathlib import Path


def _make_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return buf.getvalue()


def _create_project(client, code: str) -> str:
    resp = client.post("/projects", json={"project_code": code, "name": code})
    return resp.json()["data"]["id"]


def test_create_and_list_dataset_versions(client):
    project_id = _create_project(client, "DS_TEST")

    resp = client.post(f"/projects/{project_id}/datasets", json={})
    assert resp.status_code == 201
    first = resp.json()["data"]
    assert first["version_no"] == 1
    assert first["status"] == "CREATED"

    resp = client.post(f"/projects/{project_id}/datasets", json={"description": "second batch"})
    assert resp.json()["data"]["version_no"] == 2

    resp = client.get(f"/projects/{project_id}/datasets")
    assert len(resp.json()["data"]) == 2


def test_dataset_version_isolated_by_project(client):
    p1 = _create_project(client, "P1")
    p2 = _create_project(client, "P2")
    dv = client.post(f"/projects/{p1}/datasets", json={}).json()["data"]

    resp = client.get(f"/projects/{p2}/datasets/{dv['id']}")
    assert resp.status_code == 404


def test_create_dataset_version_requires_existing_project(client):
    resp = client.post(f"/projects/{uuid.uuid4()}/datasets", json={})
    assert resp.status_code == 404


def test_upload_zip_transitions_to_uploaded_and_extracts_files(client):
    project_id = _create_project(client, "UPLOAD_TEST")
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]

    zip_bytes = _make_zip({"images/a.jpg": b"fake-image-bytes", "labels/a.txt": b"0 0.5 0.5 0.1 0.1"})
    resp = client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("dataset.zip", zip_bytes, "application/zip")},
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["status"] == "UPLOADED"

    raw_dir = Path(body["storage_path"]) / "raw"
    assert (raw_dir / "images" / "a.jpg").read_bytes() == b"fake-image-bytes"
    assert (raw_dir / "labels" / "a.txt").exists()


def test_upload_rejects_non_zip(client):
    project_id = _create_project(client, "BADUP")
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]

    resp = client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("dataset.txt", b"not a zip", "text/plain")},
    )
    assert resp.status_code == 422


def test_upload_rejects_zip_slip(client):
    project_id = _create_project(client, "ZIPSLIP")
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../../evil.txt", b"pwned")

    resp = client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("evil.zip", buf.getvalue(), "application/zip")},
    )
    assert resp.status_code == 422
    # status should have reverted to CREATED, not stuck at UPLOADING
    resp = client.get(f"/projects/{project_id}/datasets/{dv['id']}")
    assert resp.json()["data"]["status"] == "CREATED"


def test_reupload_allowed_from_uploaded_status(client):
    project_id = _create_project(client, "REUPLOAD")
    dv = client.post(f"/projects/{project_id}/datasets", json={}).json()["data"]

    zip_bytes = _make_zip({"a.jpg": b"x"})
    resp = client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("d.zip", zip_bytes, "application/zip")},
    )
    assert resp.status_code == 200
    resp = client.post(
        f"/projects/{project_id}/datasets/{dv['id']}/upload",
        files={"file": ("d.zip", zip_bytes, "application/zip")},
    )
    assert resp.status_code == 200
