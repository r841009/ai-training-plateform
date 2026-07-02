import uuid


def test_list_base_models_returns_seeded_data(client):
    resp = client.get("/base-models")
    assert resp.status_code == 200
    names = {m["name"] for m in resp.json()["data"]}
    assert names == {"yolov8n", "yolov8s", "yolov11n", "resnet50", "efficientnet", "unet"}


def test_get_base_model_by_id(client):
    listed = client.get("/base-models").json()["data"]
    target = next(m for m in listed if m["name"] == "yolov8s")

    resp = client.get(f"/base-models/{target['id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["family"] == "yolov8"


def test_get_missing_base_model_returns_404(client):
    resp = client.get(f"/base-models/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_list_trainers_returns_seeded_data(client):
    resp = client.get("/trainers")
    assert resp.status_code == 200
    names = {t["trainer_name"] for t in resp.json()["data"]}
    assert names == {"yolo_trainer", "mock_trainer"}

    yolo = next(t for t in resp.json()["data"] if t["trainer_name"] == "yolo_trainer")
    assert yolo["supported_resume"] is True
    assert yolo["supported_export_formats"] == ["onnx", "torchscript"]


def test_get_missing_trainer_returns_404(client):
    resp = client.get(f"/trainers/{uuid.uuid4()}")
    assert resp.status_code == 404
