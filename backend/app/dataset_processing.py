"""Dataset validation + manifest/split generation. Pure filesystem logic, no DB access.

Expects the uploaded dataset to follow raw/images/ + raw/labels/ (mirrored subpaths,
YOLO-style label per image: "class_id cx cy w h" normalized to [0, 1] per line).
"""

import hashlib
import json
import random
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from PIL import Image, UnidentifiedImageError

from app.schemas.manifest import DatasetManifestEntry, DatasetValidationReport, InvalidFileEntry

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def validate_image(path: Path) -> tuple[bool, str | None, tuple[int, int] | None]:
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:  # verify() invalidates the handle; reopen to read size
            size = img.size
        return True, None, size
    except (UnidentifiedImageError, OSError) as exc:
        return False, str(exc), None


def parse_yolo_label(path: Path) -> tuple[list[int], str | None]:
    if not path.exists():
        return [], "label file not found"
    class_ids: list[int] = []
    for lineno, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 5:
            return [], f"line {lineno}: expected 5 fields, got {len(parts)}"
        class_id_str, *bbox = parts
        if not class_id_str.isdigit():
            return [], f"line {lineno}: class_id must be a non-negative integer"
        try:
            values = [float(v) for v in bbox]
        except ValueError:
            return [], f"line {lineno}: bbox values must be numeric"
        if not all(0.0 <= v <= 1.0 for v in values):
            return [], f"line {lineno}: bbox values must be within [0, 1]"
        class_ids.append(int(class_id_str))
    return class_ids, None


@dataclass
class ValidationOutcome:
    manifest_entries: list[DatasetManifestEntry] = field(default_factory=list)
    invalid_entries: list[InvalidFileEntry] = field(default_factory=list)
    class_distribution: Counter = field(default_factory=Counter)


@dataclass
class ProcessingResult:
    status: str
    report: DatasetValidationReport


def validate_dataset(storage_path: Path) -> ValidationOutcome:
    images_dir = storage_path / "raw" / "images"
    labels_dir = storage_path / "raw" / "labels"
    outcome = ValidationOutcome()

    if not images_dir.is_dir():
        outcome.invalid_entries.append(InvalidFileEntry(path="raw/images", reason="images directory not found"))
        return outcome

    for img_path in sorted(images_dir.rglob("*")):
        if not img_path.is_file() or img_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        rel = img_path.relative_to(images_dir)
        label_path = labels_dir / rel.with_suffix(".txt")

        ok, reason, size = validate_image(img_path)
        if not ok:
            outcome.invalid_entries.append(
                InvalidFileEntry(path=str(img_path.relative_to(storage_path)), reason=f"unreadable image: {reason}")
            )
            continue

        class_ids, label_error = parse_yolo_label(label_path)
        if label_error:
            outcome.invalid_entries.append(
                InvalidFileEntry(path=str(label_path.relative_to(storage_path)), reason=label_error)
            )
            continue

        width, height = size
        checksum = "sha256:" + hashlib.sha256(img_path.read_bytes()).hexdigest()
        outcome.manifest_entries.append(
            DatasetManifestEntry(
                image_id=str(rel.with_suffix("")).replace("\\", "/"),
                image_path=str(img_path.relative_to(storage_path)),
                label_path=str(label_path.relative_to(storage_path)),
                split="",  # assigned in finalize_dataset
                width=width,
                height=height,
                class_ids=class_ids,
                checksum=checksum,
            )
        )
        outcome.class_distribution.update(class_ids)

    return outcome


def assign_splits(image_ids: list[str], train_ratio: float, val_ratio: float, seed: int = 42) -> dict[str, str]:
    # ponytail: uniform random split; stratify by class_ids if class imbalance across splits becomes a problem
    shuffled = image_ids[:]
    random.Random(seed).shuffle(shuffled)
    n_train = round(len(shuffled) * train_ratio)
    n_val = round(len(shuffled) * val_ratio)
    return {
        image_id: ("train" if i < n_train else "val" if i < n_train + n_val else "test")
        for i, image_id in enumerate(shuffled)
    }


def _write_validation_report(validation_dir: Path, report: DatasetValidationReport, invalid_entries: list[InvalidFileEntry]) -> None:
    (validation_dir / "validation_report.json").write_text(report.model_dump_json(indent=2))
    (validation_dir / "invalid_files.json").write_text(json.dumps([e.model_dump() for e in invalid_entries], indent=2))


def _build_validation_report(
    dataset_version_id: UUID,
    total_files: int,
    valid_files: int,
    invalid_files: int,
    class_distribution: dict[str, int],
) -> DatasetValidationReport:
    return DatasetValidationReport(
        dataset_version_id=dataset_version_id,
        total_files=total_files,
        valid_files=valid_files,
        invalid_files=invalid_files,
        class_distribution=class_distribution,
        generated_at=datetime.now(timezone.utc),
    )


def write_invalid_report(storage_path: Path, dataset_version_id: UUID, outcome: ValidationOutcome) -> ProcessingResult:
    report = _build_validation_report(
        dataset_version_id=dataset_version_id,
        total_files=len(outcome.invalid_entries),
        valid_files=0,
        invalid_files=len(outcome.invalid_entries),
        class_distribution={},
    )
    _write_validation_report(storage_path / "validation", report, outcome.invalid_entries)
    return ProcessingResult(status="INVALID", report=report)


def finalize_dataset(
    storage_path: Path,
    dataset_version_id: UUID,
    outcome: ValidationOutcome,
    class_names: dict[int, str] | None,
    train_ratio: float,
    val_ratio: float,
) -> ProcessingResult:
    splits = assign_splits([e.image_id for e in outcome.manifest_entries], train_ratio, val_ratio)
    for entry in outcome.manifest_entries:
        entry.split = splits[entry.image_id]

    manifests_dir = storage_path / "manifests"
    with (manifests_dir / "dataset_manifest.jsonl").open("w") as f:
        for entry in outcome.manifest_entries:
            f.write(entry.model_dump_json() + "\n")

    class_names = class_names or {}
    class_mapping = {
        str(class_id): class_names.get(class_id, f"class_{class_id}") for class_id in sorted(outcome.class_distribution)
    }
    (manifests_dir / "class_mapping.json").write_text(json.dumps(class_mapping, indent=2))

    split_files: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    for entry in outcome.manifest_entries:
        split_files[entry.split].append(entry.image_id)
    for split_name, ids in split_files.items():
        (storage_path / "splits" / f"{split_name}.txt").write_text("\n".join(ids) + ("\n" if ids else ""))

    total_files = len(outcome.manifest_entries) + len(outcome.invalid_entries)
    statistics = {
        "total_files": total_files,
        "valid_files": len(outcome.manifest_entries),
        "invalid_files": len(outcome.invalid_entries),
        "split_counts": {k: len(v) for k, v in split_files.items()},
        "class_distribution": {str(k): v for k, v in outcome.class_distribution.items()},
    }
    (manifests_dir / "dataset_statistics.json").write_text(json.dumps(statistics, indent=2))

    report = _build_validation_report(
        dataset_version_id=dataset_version_id,
        total_files=total_files,
        valid_files=len(outcome.manifest_entries),
        invalid_files=len(outcome.invalid_entries),
        class_distribution={str(k): v for k, v in outcome.class_distribution.items()},
    )
    _write_validation_report(storage_path / "validation", report, outcome.invalid_entries)

    return ProcessingResult(status="READY", report=report)
