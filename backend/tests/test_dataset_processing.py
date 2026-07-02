import json
import uuid
from pathlib import Path

from PIL import Image

from app.dataset_processing import (
    assign_splits,
    finalize_dataset,
    parse_yolo_label,
    validate_dataset,
    validate_image,
    write_invalid_report,
)


def _make_image(path: Path, size=(32, 32)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color="red").save(path)


def test_validate_image_accepts_real_image(tmp_path):
    img_path = tmp_path / "a.jpg"
    _make_image(img_path)
    ok, reason, size = validate_image(img_path)
    assert ok is True
    assert reason is None
    assert size == (32, 32)


def test_validate_image_rejects_corrupt_file(tmp_path):
    bad_path = tmp_path / "bad.jpg"
    bad_path.write_bytes(b"not an image")
    ok, reason, size = validate_image(bad_path)
    assert ok is False
    assert reason is not None


def test_parse_yolo_label_valid(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("0 0.5 0.5 0.2 0.2\n1 0.1 0.1 0.05 0.05\n")
    class_ids, error = parse_yolo_label(p)
    assert error is None
    assert class_ids == [0, 1]


def test_parse_yolo_label_missing_file(tmp_path):
    class_ids, error = parse_yolo_label(tmp_path / "missing.txt")
    assert class_ids == []
    assert error == "label file not found"


def test_parse_yolo_label_rejects_bad_field_count(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("0 0.5 0.5\n")
    class_ids, error = parse_yolo_label(p)
    assert class_ids == []
    assert "expected 5 fields" in error


def test_parse_yolo_label_rejects_out_of_range_bbox(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("0 1.5 0.5 0.2 0.2\n")
    class_ids, error = parse_yolo_label(p)
    assert class_ids == []
    assert "within [0, 1]" in error


def test_parse_yolo_label_allows_empty_file_as_no_objects(tmp_path):
    p = tmp_path / "a.txt"
    p.write_text("")
    class_ids, error = parse_yolo_label(p)
    assert class_ids == []
    assert error is None


def test_assign_splits_proportions_roughly_correct():
    image_ids = [f"img_{i}" for i in range(100)]
    splits = assign_splits(image_ids, train_ratio=0.7, val_ratio=0.2)
    counts = {"train": 0, "val": 0, "test": 0}
    for split in splits.values():
        counts[split] += 1
    assert counts["train"] == 70
    assert counts["val"] == 20
    assert counts["test"] == 10


def _build_sample_dataset(storage_path: Path, n_good: int = 3, n_bad_label: int = 1, n_bad_image: int = 1) -> None:
    for sub in ("raw/images", "raw/labels", "manifests", "splits", "validation"):
        (storage_path / sub).mkdir(parents=True, exist_ok=True)

    for i in range(n_good):
        _make_image(storage_path / "raw" / "images" / f"good_{i}.jpg")
        (storage_path / "raw" / "labels" / f"good_{i}.txt").write_text("0 0.5 0.5 0.2 0.2\n")

    for i in range(n_bad_label):
        _make_image(storage_path / "raw" / "images" / f"badlabel_{i}.jpg")
        (storage_path / "raw" / "labels" / f"badlabel_{i}.txt").write_text("not a valid label\n")

    for i in range(n_bad_image):
        (storage_path / "raw" / "images" / f"badimage_{i}.jpg").write_bytes(b"garbage")
        (storage_path / "raw" / "labels" / f"badimage_{i}.txt").write_text("0 0.5 0.5 0.2 0.2\n")


def test_validate_and_finalize_dataset_writes_expected_outputs(tmp_path):
    _build_sample_dataset(tmp_path, n_good=7, n_bad_label=1, n_bad_image=1)

    outcome = validate_dataset(tmp_path)
    assert len(outcome.manifest_entries) == 7
    assert len(outcome.invalid_entries) == 2

    result = finalize_dataset(tmp_path, uuid.uuid4(), outcome, class_names={0: "scratch"}, train_ratio=0.7, val_ratio=0.2)
    assert result.status == "READY"

    manifest_lines = (tmp_path / "manifests" / "dataset_manifest.jsonl").read_text().strip().splitlines()
    assert len(manifest_lines) == 7

    class_mapping = json.loads((tmp_path / "manifests" / "class_mapping.json").read_text())
    assert class_mapping == {"0": "scratch"}

    stats = json.loads((tmp_path / "manifests" / "dataset_statistics.json").read_text())
    assert stats["valid_files"] == 7
    assert stats["invalid_files"] == 2
    assert sum(stats["split_counts"].values()) == 7

    invalid_files = json.loads((tmp_path / "validation" / "invalid_files.json").read_text())
    assert len(invalid_files) == 2


def test_validate_dataset_missing_images_dir_returns_no_entries(tmp_path):
    outcome = validate_dataset(tmp_path)
    assert outcome.manifest_entries == []
    assert len(outcome.invalid_entries) == 1


def test_write_invalid_report(tmp_path):
    (tmp_path / "validation").mkdir(parents=True)
    outcome = validate_dataset(tmp_path)  # empty dir -> 1 invalid entry (missing images dir)
    result = write_invalid_report(tmp_path, uuid.uuid4(), outcome)
    assert result.status == "INVALID"
    report = json.loads((tmp_path / "validation" / "validation_report.json").read_text())
    assert report["valid_files"] == 0
