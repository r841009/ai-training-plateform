# Phase 10：Training Script 第一版

日期：2026-07-06

## 目標

建立第一版 mock training script，支援 `training_config.json`、`job_id`、`dataset_manifest.jsonl`、`metrics.jsonl`、`checkpoint_latest.pt`、`checkpoint_best.pt` 與 `resume` flag。不接真實 YOLO。

## 已完成項目

- 新增 `trainers/mock_train.py`。
- 支援 CLI：

```powershell
.\backend\.venv\Scripts\python.exe -m trainers.mock_train `
  --config training_config.json `
  --job-id <training_job_id> `
  --manifest dataset_manifest.jsonl `
  --output-dir <job_output_dir> `
  [--resume]
```

- `training_config.json` 目前讀取：
  - `epochs`，預設 `1`
- `dataset_manifest.jsonl` 逐行讀取，並計算 sample 數與 split counts。
- 每個 epoch 會 append/write 一行 `metrics.jsonl`。
- 每個 epoch 會更新 `checkpoint_latest.pt`。
- 當 `val_loss` 改善時更新 `checkpoint_best.pt`。
- `--resume` 會讀取既有 `checkpoint_latest.pt` 的 epoch，從下一個 epoch 接續並 append metrics。

## 產生 / 修改的檔案

```text
trainers/__init__.py
trainers/mock_train.py
backend/tests/test_mock_train.py
README.md
worker/README.md
develope-log/phase-10.md
```

## 已知限制

- `.pt` checkpoint 目前是 JSON 內容，檔名先對齊未來 PyTorch checkpoint 介面。
- Worker Manager 尚未改成 subprocess 執行 `trainers/mock_train.py`；Phase 9 的內建 runner 仍保留。
- 尚未建立 `checkpoints` table，留到 Phase 11。

## 如何測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_mock_train.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：

- `tests/test_mock_train.py`：`2 passed`
- 全量 backend tests：`62 passed`
- Alembic head：`c1d2e3f4a5b6`
