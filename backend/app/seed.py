"""Idempotent seed data for platform-level catalogs. Run: python -m app.seed"""

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.base_model import BaseModelEntry
from app.models.trainer import Trainer

BASE_MODELS = [
    {"name": "yolov8n", "family": "yolov8", "task_type": "detection"},
    {"name": "yolov8s", "family": "yolov8", "task_type": "detection"},
    {"name": "yolov11n", "family": "yolov11", "task_type": "detection"},
    {"name": "resnet50", "family": "resnet", "task_type": "classification"},
    {"name": "efficientnet", "family": "efficientnet", "task_type": "classification"},
    {"name": "unet", "family": "unet", "task_type": "segmentation"},
]

TRAINERS = [
    {
        "trainer_name": "yolo_trainer",
        "task_type": "detection",
        "base_model_family": "yolov8",
        "entrypoint": "python trainers/yolo_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx", "torchscript"],
    },
    {
        "trainer_name": "mock_trainer",
        "task_type": "detection",
        "base_model_family": "*",
        "entrypoint": "python trainers/mock_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": [],
    },
]


def seed(db: Session) -> None:
    existing_models = {m.name for m in db.query(BaseModelEntry).all()}
    for row in BASE_MODELS:
        if row["name"] not in existing_models:
            db.add(BaseModelEntry(**row))

    existing_trainers = {t.trainer_name for t in db.query(Trainer).all()}
    for row in TRAINERS:
        if row["trainer_name"] not in existing_trainers:
            db.add(Trainer(**row))

    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()
    print("seed complete")
