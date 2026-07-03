import uuid


def test_list_base_models_returns_seeded_data(client):
    resp = client.get("/base-models")
    assert resp.status_code == 200
    names = {m["name"] for m in resp.json()["data"]}
    assert {
        "yolov8n",
        "yolov8s",
        "yolov11n",
        "resnet50",
        "efficientnet",
        "unet",
        "fasterrcnn_resnet50_fpn",
        "retinanet_resnet50_fpn",
        "ssd300_vgg16",
        "fcos_resnet50_fpn",
        "yolox_s",
        "yolox_m",
        "detectron2_fasterrcnn_r50_fpn",
        "detectron2_retinanet_r50_fpn",
        "detr_resnet50",
        "rt_detr_r50",
        "mmdet_retinanet_r50_fpn",
    }.issubset(names)


def test_base_model_license_metadata_marks_yolo_as_restricted(client):
    listed = client.get("/base-models").json()["data"]
    yolo = next(m for m in listed if m["name"] == "yolov8s")
    assert yolo["source_provider"] == "Ultralytics"
    assert yolo["license_risk_level"] == "HIGH"
    assert yolo["requires_enterprise_license"] is True
    assert yolo["oem_use_allowed"] is False


def test_base_model_license_metadata_includes_oem_safe_alternatives(client):
    listed = client.get("/base-models").json()["data"]
    yolox = next(m for m in listed if m["name"] == "yolox_s")
    assert yolox["license_name"] == "Apache-2.0"
    assert yolox["license_risk_level"] == "LOW"
    assert yolox["oem_use_allowed"] is True
    assert yolox["requires_enterprise_license"] is False


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
    assert {
        "yolo_trainer",
        "mock_trainer",
        "torchvision_detection_trainer",
        "yolox_trainer",
        "detectron2_trainer",
        "mmdetection_trainer",
        "paddledetection_trainer",
        "detr_trainer",
    }.issubset(names)

    yolo = next(t for t in resp.json()["data"] if t["trainer_name"] == "yolo_trainer")
    assert yolo["supported_resume"] is True
    assert yolo["supported_export_formats"] == ["onnx", "torchscript"]


def test_get_missing_trainer_returns_404(client):
    resp = client.get(f"/trainers/{uuid.uuid4()}")
    assert resp.status_code == 404
