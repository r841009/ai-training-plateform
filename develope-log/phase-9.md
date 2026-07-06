# Phase 9：Worker Manager

日期：2026-07-06

## 目標

建立 Worker Manager 第一版，讓它可以取得 Scheduler 已派工的 `DISPATCHED` job，執行 mock trainer，回報 heartbeat，更新 job status，並捕捉 log。不實作 checkpoint、Model Version 或 retrain。

## 已完成項目

- 建立 `worker/worker_manager.py`。
- 建立 `WorkerManager.run_once()`，可針對指定 `training_server_id` 取得 `DISPATCHED` jobs。
- 建立內建 `MockTrainerRunner`，使用 `training_config_json` 模擬訓練：
  - `epochs`
  - `mock_success`
  - `mock_failure_reason`
- Worker 執行流程：
  - `DISPATCHED` → `RUNNING`
  - mock trainer 成功：`RUNNING` → `SUCCESS`
  - mock trainer 失敗或 exception：`RUNNING` → `FAILED`
- Worker 會更新 Training Server heartbeat。
- Worker 完成 terminal status 後會釋放 `training_servers.running_job_count`。
- Worker log 會寫到 Project-scoped storage path：

```text
{storage_root}/projects/{project_code}/training-jobs/{training_job_id}/worker.log
```

- 補上 `TrainingJobRepository.list_dispatched_for_server()`，供 worker 依 server 取得已派工 jobs。
- 新增測試涵蓋：
  - worker 成功完成 `DISPATCHED` job 並捕捉 log
  - mock trainer 失敗時 job 會轉為 `FAILED` 並保存 `failure_reason`

## 產生 / 修改的檔案

```text
worker/__init__.py
worker/worker_manager.py
worker/README.md
backend/app/repositories/training_job_repository.py
backend/tests/test_worker_manager.py
README.md
develope-log/phase-9.md
```

## 如何測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：

- `60 passed`
- Alembic head：`c1d2e3f4a5b6`

## 已知限制

- Phase 9 的 mock trainer 是 worker 內建 runner，不是獨立 training script。
- 尚未產生 `metrics.jsonl`、`checkpoint_latest.pt`、`checkpoint_best.pt`。
- 尚未建立 `checkpoints` table。
- 尚未在訓練成功後產生 Model Version。

## 下一步

Phase 10：Training Script 第一版。建議建立 `trainers/mock_train.py`，支援讀取 `training_config.json`、`job_id`、`dataset_manifest.jsonl`，並輸出 `metrics.jsonl`、`checkpoint_latest.pt`、`checkpoint_best.pt`，但仍可先用 mock training loop，不接真實 YOLO。
