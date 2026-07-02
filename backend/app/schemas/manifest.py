"""Formats written under manifests/ and validation/ by the Phase 5 dataset processing service."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class DatasetManifestEntry(BaseModel):
    image_id: str
    image_path: str
    label_path: str | None = None
    split: str
    width: int
    height: int
    class_ids: list[int]
    checksum: str
    metadata: dict = {}


class InvalidFileEntry(BaseModel):
    path: str
    reason: str


class DatasetValidationReport(BaseModel):
    dataset_version_id: uuid.UUID
    total_files: int
    valid_files: int
    invalid_files: int
    class_distribution: dict[str, int] = {}
    generated_at: datetime
