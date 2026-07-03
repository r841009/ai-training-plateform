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
    {"name": "yolox_s", "family": "yolox", "task_type": "detection", **apache_license("Megvii YOLOX", "https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE")},
    {"name": "yolox_m", "family": "yolox", "task_type": "detection", **apache_license("Megvii YOLOX", "https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE")},
    {"name": "detectron2_fasterrcnn_r50_fpn", "family": "detectron2", "task_type": "detection", **apache_license("Detectron2", "https://github.com/facebookresearch/detectron2/blob/main/LICENSE")},
    {"name": "detectron2_retinanet_r50_fpn", "family": "detectron2", "task_type": "detection", **apache_license("Detectron2", "https://github.com/facebookresearch/detectron2/blob/main/LICENSE")},
    {"name": "detr_resnet50", "family": "detr", "task_type": "detection", **apache_license("Facebook DETR", "https://github.com/facebookresearch/detr/blob/main/LICENSE")},
    {"name": "rt_detr_r50", "family": "paddledetection", "task_type": "detection", **apache_license("PaddleDetection", "https://github.com/PaddlePaddle/PaddleDetection/blob/develop/LICENSE")},
    {"name": "mmdet_retinanet_r50_fpn", "family": "mmdetection", "task_type": "detection", **apache_license("MMDetection", "https://github.com/open-mmlab/mmdetection/blob/main/LICENSE")},
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
    {
        "trainer_name": "torchvision_detection_trainer",
        "task_type": "detection",
        "base_model_family": "torchvision_detection",
        "entrypoint": "python trainers/torchvision_detection_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx", "torchscript"],
    },
    {
        "trainer_name": "yolox_trainer",
        "task_type": "detection",
        "base_model_family": "yolox",
        "entrypoint": "python trainers/yolox_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx", "torchscript"],
    },
    {
        "trainer_name": "detectron2_trainer",
        "task_type": "detection",
        "base_model_family": "detectron2",
        "entrypoint": "python trainers/detectron2_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx", "torchscript"],
    },
    {
        "trainer_name": "mmdetection_trainer",
        "task_type": "detection",
        "base_model_family": "mmdetection",
        "entrypoint": "python trainers/mmdetection_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx"],
    },
    {
        "trainer_name": "paddledetection_trainer",
        "task_type": "detection",
        "base_model_family": "paddledetection",
        "entrypoint": "python trainers/paddledetection_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx"],
    },
    {
        "trainer_name": "detr_trainer",
        "task_type": "detection",
        "base_model_family": "detr",
        "entrypoint": "python trainers/detr_train.py",
        "docker_image": None,
        "supported_resume": True,
        "supported_export_formats": ["onnx", "torchscript"],
    },
]


def seed(db: Session) -> None:
    existing_models = {m.name: m for m in db.query(BaseModelEntry).all()}
    for row in BASE_MODELS:
        existing = existing_models.get(row["name"])
        if existing is None:
            db.add(BaseModelEntry(**row))
        else:
            for key, value in row.items():
                setattr(existing, key, value)

    existing_trainers = {t.trainer_name: t for t in db.query(Trainer).all()}
    for row in TRAINERS:
        existing = existing_trainers.get(row["trainer_name"])
        if existing is None:
            db.add(Trainer(**row))
        else:
            for key, value in row.items():
                setattr(existing, key, value)

    db.commit()


if __name__ == "__main__":
    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()
    print("seed complete")
