from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def _read_manifest(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _split_counts(entries: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"train": 0, "val": 0, "test": 0}
    for entry in entries:
        split = entry.get("split", "")
        counts[split] = counts.get(split, 0) + 1
    return counts


def _checkpoint_epoch(path: Path) -> int:
    if not path.exists():
        return 0
    return int(json.loads(path.read_text()).get("epoch", 0))


def _write_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2))


def run_mock_training(
    config_path: Path,
    job_id: uuid.UUID,
    manifest_path: Path,
    output_dir: Path,
    resume: bool = False,
) -> dict[str, Any]:
    config = _read_json(config_path)
    entries = _read_manifest(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    epochs = max(1, int(config.get("epochs", 1) or 1))
    latest_path = output_dir / "checkpoint_latest.pt"
    best_path = output_dir / "checkpoint_best.pt"
    metrics_path = output_dir / "metrics.jsonl"
    start_epoch = _checkpoint_epoch(latest_path) + 1 if resume else 1
    best_val_loss = float("inf")

    with metrics_path.open("a" if resume else "w") as metrics_file:
        for epoch in range(start_epoch, epochs + 1):
            train_loss = round(1 / epoch, 6)
            val_loss = round(1 / (epoch + 1), 6)
            metric = {
                "job_id": str(job_id),
                "epoch": epoch,
                "epochs": epochs,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "samples": len(entries),
                "split_counts": _split_counts(entries),
                "resumed": resume,
            }
            metrics_file.write(json.dumps(metric) + "\n")

            checkpoint = {
                "job_id": str(job_id),
                "epoch": epoch,
                "epochs": epochs,
                "best_val_loss": min(best_val_loss, val_loss),
                "training_config": config,
                "manifest_path": str(manifest_path),
            }
            _write_checkpoint(latest_path, checkpoint)
            if val_loss <= best_val_loss:
                best_val_loss = val_loss
                _write_checkpoint(best_path, checkpoint)

    return {
        "job_id": str(job_id),
        "epochs": epochs,
        "samples": len(entries),
        "metrics_path": str(metrics_path),
        "checkpoint_latest_path": str(latest_path),
        "checkpoint_best_path": str(best_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mock training loop for Phase 10.")
    parser.add_argument("--config", required=True, type=Path, help="Path to training_config.json")
    parser.add_argument("--job-id", required=True, type=uuid.UUID)
    parser.add_argument("--manifest", required=True, type=Path, help="Path to dataset_manifest.jsonl")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(
        json.dumps(
            run_mock_training(args.config, args.job_id, args.manifest, args.output_dir, args.resume),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
