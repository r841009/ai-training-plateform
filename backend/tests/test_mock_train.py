import json
import uuid

from trainers.mock_train import run_mock_training


def _write_manifest(path, count: int = 3) -> None:
    rows = [
        {
            "image_id": f"img_{i}",
            "image_path": f"processed/images/img_{i}.jpg",
            "label_path": f"processed/labels/img_{i}.txt",
            "split": "train" if i < count - 1 else "val",
            "width": 16,
            "height": 16,
            "class_ids": [0],
            "checksum": f"checksum-{i}",
            "metadata": {},
        }
        for i in range(count)
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n")


def test_mock_train_writes_metrics_and_checkpoints(tmp_path):
    config_path = tmp_path / "training_config.json"
    manifest_path = tmp_path / "dataset_manifest.jsonl"
    output_dir = tmp_path / "job"
    job_id = uuid.uuid4()
    config_path.write_text(json.dumps({"epochs": 2, "batch_size": 4}))
    _write_manifest(manifest_path)

    result = run_mock_training(config_path, job_id, manifest_path, output_dir)

    metrics = [json.loads(line) for line in (output_dir / "metrics.jsonl").read_text().splitlines()]
    latest = json.loads((output_dir / "checkpoint_latest.pt").read_text())
    best = json.loads((output_dir / "checkpoint_best.pt").read_text())
    assert result["job_id"] == str(job_id)
    assert [m["epoch"] for m in metrics] == [1, 2]
    assert metrics[-1]["samples"] == 3
    assert metrics[-1]["split_counts"] == {"train": 2, "val": 1, "test": 0}
    assert latest["epoch"] == 2
    assert best["epoch"] == 2


def test_mock_train_resume_appends_from_latest_checkpoint(tmp_path):
    config_path = tmp_path / "training_config.json"
    manifest_path = tmp_path / "dataset_manifest.jsonl"
    output_dir = tmp_path / "job"
    job_id = uuid.uuid4()
    config_path.write_text(json.dumps({"epochs": 3}))
    _write_manifest(manifest_path, count=1)
    run_mock_training(config_path, job_id, manifest_path, output_dir)

    config_path.write_text(json.dumps({"epochs": 4}))
    run_mock_training(config_path, job_id, manifest_path, output_dir, resume=True)

    metrics = [json.loads(line) for line in (output_dir / "metrics.jsonl").read_text().splitlines()]
    latest = json.loads((output_dir / "checkpoint_latest.pt").read_text())
    assert [m["epoch"] for m in metrics] == [1, 2, 3, 4]
    assert metrics[-1]["resumed"] is True
    assert latest["epoch"] == 4
