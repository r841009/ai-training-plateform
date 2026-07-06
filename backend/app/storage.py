import zipfile
from pathlib import Path

from app.config import get_settings

DATASET_SUBDIRS = ("raw", "processed", "splits", "manifests", "validation")


def dataset_storage_path(project_code: str, version_no: int) -> Path:
    return Path(get_settings().storage_root) / "projects" / project_code / "datasets" / f"v{version_no}"


def ensure_dataset_dirs(base: Path) -> None:
    for sub in DATASET_SUBDIRS:
        (base / sub).mkdir(parents=True, exist_ok=True)


def safe_extract_zip(zip_path: Path, dest: Path) -> None:
    """Extract zip_path into dest, rejecting entries that escape dest (zip-slip)."""
    dest = dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            member_path = (dest / member.filename).resolve()
            if member_path != dest and dest not in member_path.parents:
                raise ValueError(f"unsafe zip entry escapes destination: {member.filename}")
        zf.extractall(dest)
