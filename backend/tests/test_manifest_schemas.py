import uuid
from datetime import datetime, timezone

from app.schemas.manifest import DatasetManifestEntry, DatasetValidationReport, InvalidFileEntry


def test_dataset_manifest_entry_round_trip():
    entry = DatasetManifestEntry(
        image_id="img_0001",
        image_path="raw/images/a.jpg",
        label_path="raw/labels/a.txt",
        split="train",
        width=640,
        height=480,
        class_ids=[0, 2],
        checksum="sha256:deadbeef",
    )
    restored = DatasetManifestEntry.model_validate_json(entry.model_dump_json())
    assert restored == entry


def test_dataset_validation_report_round_trip():
    report = DatasetValidationReport(
        dataset_version_id=uuid.uuid4(),
        total_files=10,
        valid_files=9,
        invalid_files=1,
        class_distribution={"scratch": 7, "stain": 2},
        generated_at=datetime.now(timezone.utc),
    )
    restored = DatasetValidationReport.model_validate_json(report.model_dump_json())
    assert restored == report
    assert InvalidFileEntry(path="raw/images/bad.jpg", reason="unreadable").reason == "unreadable"
