import uuid


def test_create_and_get_project(client):
    resp = client.post("/projects", json={"project_code": "LED_SCRATCH", "name": "LED Scratch Detection"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["project_code"] == "LED_SCRATCH"

    project_id = body["data"]["id"]
    resp = client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["project_code"] == "LED_SCRATCH"


def test_duplicate_project_code_rejected(client):
    client.post("/projects", json={"project_code": "PCB_STAIN", "name": "PCB Stain"})
    resp = client.post("/projects", json={"project_code": "PCB_STAIN", "name": "Dup"})
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_invalid_project_code_rejected(client):
    resp = client.post("/projects", json={"project_code": "bad code!", "name": "x"})
    assert resp.status_code == 422


def test_list_update_and_delete_project(client):
    resp = client.post("/projects", json={"project_code": "X1", "name": "orig"})
    project_id = resp.json()["data"]["id"]

    resp = client.get("/projects")
    assert len(resp.json()["data"]) == 1

    resp = client.patch(f"/projects/{project_id}", json={"name": "updated"})
    assert resp.json()["data"]["name"] == "updated"
    assert resp.json()["data"]["project_code"] == "X1"  # immutable

    resp = client.delete(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert client.get(f"/projects/{project_id}").status_code == 404


def test_get_missing_project(client):
    resp = client.get(f"/projects/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["success"] is False
