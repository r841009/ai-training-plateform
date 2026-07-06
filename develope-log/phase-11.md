# Phase 11：Checkpoint / Resume

日期：2026-07-06

## 目標

建立 checkpoints table，讓 Worker 中斷時可標記 `INTERRUPTED` / `RESUMABLE`，並提供 resume API 讓 Scheduler 可重新派工。

## 已完成項目

- 新增 `checkpoints` table：
  - `project_id`
  - `training_job_id`
  - `checkpoint_path`
  - `epoch`
  - `metrics_json`
  - `is_latest`
  - `is_best`
  - `created_at`
- 新增 `Checkpoint` model 與 `CheckpointRepository`。
- Training Job 新增 resume API：

```text
POST /projects/{project_id}/training-jobs/{training_job_id}/resume
```

- Resume API 行為：
  - 只允許 `INTERRUPTED` / `FAILED` / `RESUMABLE` job
  - 必須存在 `checkpoint_latest.pt`
  - 將 job 標為 `RESUMABLE`
  - 清空 `assigned_server_id` / `failure_reason`
  - 在 `training_config_json` 寫入 `resume: true`
- Scheduler 會掃描 `PENDING` / `QUEUED` / `RESUMABLE` jobs。
- Worker 若捕捉到 `KeyboardInterrupt`：
  - 先標記 `INTERRUPTED`
  - 若 job output 目錄存在 `checkpoint_latest.pt`，寫入 checkpoint row 並標記 `RESUMABLE`
  - 釋放 Training Server `running_job_count`
- Worker 重新執行 resume job 時，會把 `checkpoint_latest_path` 放進 `training_config_json`，mock runner 會從 checkpoint epoch 下一個 epoch 接續。

## 產生 / 修改的檔案

```text
backend/app/models/checkpoint.py
backend/app/repositories/checkpoint_repository.py
backend/alembic/versions/d2e3f4a5b6c7_create_checkpoints_table.py
backend/app/models/__init__.py
backend/app/repositories/training_job_repository.py
backend/app/services/training_job_service.py
backend/app/routers/training_jobs.py
backend/tests/test_worker_manager.py
worker/worker_manager.py
README.md
worker/README.md
develope-log/phase-11.md
```

## 如何測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_worker_manager.py tests\test_training_jobs.py tests\test_scheduler.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：

- `tests/test_worker_manager.py tests/test_training_jobs.py tests/test_scheduler.py`：`17 passed`
- 全量 backend tests：`65 passed`
- Alembic head：`d2e3f4a5b6c7`

## 已知限制

- Worker 目前仍使用 Phase 9 的內建 mock runner，尚未改成 subprocess 執行 `trainers/mock_train.py`。
- Checkpoint row 目前只在 Worker 中斷且找到 `checkpoint_latest.pt` 時寫入。
- `checkpoint_best.pt` 的資料表紀錄留到真實 trainer / model version 流程再補。

## 下一步

Phase 12：Model Version 模組。訓練成功後產生 Project-scoped Model Version。
