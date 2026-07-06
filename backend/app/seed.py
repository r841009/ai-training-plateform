"""Idempotent seed data for platform-level catalogs. Run: python -m app.seed"""

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.base_model import BaseModelEntry
from app.models.trainer import Trainer

ULTRALYTICS_LICENSE_URL = "https://www.ultralytics.com/license"
TORCHVISION_LICENSE_URL = "https://github.com/pytorch/vision/blob/main/LICENSE"
APACHE_2_LICENSE_URL = "https://www.apache.org/licenses/LICENSE-2.0"

YOLO_LICENSE = {
    "source_provider": "Ultralytics",
    "license_name": "AGPL-3.0 / Ultralytics Enterprise License",
    "license_url": ULTRALYTICS_LICENSE_URL,
    "license_risk_level": "HIGH",
    "commercial_use_allowed": False,
    "oem_use_allowed": False,
    "requires_enterprise_license": True,
    "license_notes": (
        "Do not use in OEM/proprietary/customer-facing deployments unless an Ultralytics "
        "Enterprise License covers the project."
    ),
}

TORCHVISION_LICENSE = {
    "source_provider": "torchvision",
    "license_name": "BSD-3-Clause",
    "license_url": TORCHVISION_LICENSE_URL,
    "license_risk_level": "LOW",
    "commercial_use_allowed": True,
    "oem_use_allowed": True,
    "requires_enterprise_license": False,
    "license_notes": "Permissive license; retain required copyright and license notices.",
}


def apache_license(provider: str, license_url: str = APACHE_2_LICENSE_URL) -> dict:
    return {
        "source_provider": provider,
        "license_name": "Apache-2.0",
        "license_url": license_url,
        "license_risk_level": "LOW",
        "commercial_use_allowed": True,
        "oem_use_allowed": True,
        "requires_enterprise_license": False,
        "license_notes": "Permissive license; retain required copyright, license, and NOTICE files.",
    }


YOLOX_LICENSE = apache_license("Megvii YOLOX", "https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE")
DETECTRON2_LICENSE = apache_license("Detectron2", "https://github.com/facebookresearch/detectron2/blob/main/LICENSE")
DETR_LICENSE = apache_license("Facebook DETR", "https://github.com/facebookresearch/detr/blob/main/LICENSE")
PADDLEDETECTION_LICENSE = apache_license(
    "PaddleDetection", "https://github.com/PaddlePaddle/PaddleDetection/blob/develop/LICENSE"
)
MMDETECTION_LICENSE = apache_license("MMDetection", "https://github.com/open-mmlab/mmdetection/blob/main/LICENSE")
DEFAULT_EXPORT_FORMATS = ["onnx", "torchscript"]


def trainer_row(
    trainer_name: str,
    base_model_family: str,
    entrypoint: str,
    export_formats: list[str] | None = None,
) -> dict:
    return {
        "trainer_name": trainer_name,
        "task_type": "detection",
        "base_model_family": base_model_family,
        "entrypoint": entrypoint,
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": list(DEFAULT_EXPORT_FORMATS if export_formats is None else export_formats),
    }


BASE_MODELS = [
    {"name": "yolov8n", "family": "yolov8", "task_type": "detection", **YOLO_LICENSE},
    {"name": "yolov8s", "family": "yolov8", "task_type": "detection", **YOLO_LICENSE},
    {"name": "yolov11n", "family": "yolov11", "task_type": "detection", **YOLO_LICENSE},
    {"name": "resnet50", "family": "resnet", "task_type": "classification", **TORCHVISION_LICENSE},
    {
        "name": "efficientnet",
        "family": "efficientnet",
        "task_type": "classification",
        **{
            **TORCHVISION_LICENSE,
            "license_notes": "Use torchvision implementation/weights or re-verify the final source before release.",
        },
    },
    {
        "name": "unet",
        "family": "unet",
        "task_type": "segmentation",
        "source_provider": "internal",
        "license_name": "Internal implementation",
        "license_url": None,
        "license_risk_level": "LOW",
        "commercial_use_allowed": True,
        "oem_use_allowed": True,
        "requires_enterprise_license": False,
        "license_notes": "Use company-owned implementation/weights or re-verify any third-party implementation before release.",
    },
    {"name": "fasterrcnn_resnet50_fpn", "family": "torchvision_detection", "task_type": "detection", **TORCHVISION_LICENSE},
    {"name": "retinanet_resnet50_fpn", "family": "torchvision_detection", "task_type": "detection", **TORCHVISION_LICENSE},
    {"name": "ssd300_vgg16", "family": "torchvision_detection", "task_type": "detection", **TORCHVISION_LICENSE},
    {"name": "fcos_resnet50_fpn", "family": "torchvision_detection", "task_type": "detection", **TORCHVISION_LICENSE},
    {"name": "yolox_s", "family": "yolox", "task_type": "detection", **YOLOX_LICENSE},
    {"name": "yolox_m", "family": "yolox", "task_type": "detection", **YOLOX_LICENSE},
    {"name": "detectron2_fasterrcnn_r50_fpn", "family": "detectron2", "task_type": "detection", **DETECTRON2_LICENSE},
    {"name": "detectron2_retinanet_r50_fpn", "family": "detectron2", "task_type": "detection", **DETECTRON2_LICENSE},
    {"name": "detr_resnet50", "family": "detr", "task_type": "detection", **DETR_LICENSE},
    {"name": "rt_detr_r50", "family": "paddledetection", "task_type": "detection", **PADDLEDETECTION_LICENSE},
    {"name": "mmdet_retinanet_r50_fpn", "family": "mmdetection", "task_type": "detection", **MMDETECTION_LICENSE},
]

TRAINERS = [
    trainer_row("yolo_trainer", "yolov8", "python trainers/yolo_train.py"),
    trainer_row("mock_trainer", "*", "python trainers/mock_train.py", []),
    trainer_row(
        "torchvision_detection_trainer",
        "torchvision_detection",
        "python trainers/torchvision_detection_train.py",
    ),
    trainer_row("yolox_trainer", "yolox", "python trainers/yolox_train.py"),
    trainer_row("detectron2_trainer", "detectron2", "python trainers/detectron2_train.py"),
    trainer_row("mmdetection_trainer", "mmdetection", "python trainers/mmdetection_train.py", ["onnx"]),
    trainer_row("paddledetection_trainer", "paddledetection", "python trainers/paddledetection_train.py", ["onnx"]),
    trainer_row("detr_trainer", "detr", "python trainers/detr_train.py"),
]


def _upsert_rows(db: Session, model_cls, lookup_key: str, rows: list[dict]) -> None:
    existing_rows = {getattr(row, lookup_key): row for row in db.query(model_cls).all()}
    for row in rows:
        existing = existing_rows.get(row[lookup_key])
        if existing is None:
            db.add(model_cls(**row))
        else:
            for field, value in row.items():
                setattr(existing, field, value)


def seed(db: Session) -> None:
    _upsert_rows(db, BaseModelEntry, "name", BASE_MODELS)
    _upsert_rows(db, Trainer, "trainer_name", TRAINERS)
    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()
    print("seed complete")
