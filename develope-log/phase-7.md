# Phase 7：Training Job 模組

日期：2026-07-03

## 目標

建立 Project-scoped Training Job 模組，包含 `training_jobs` table、Training Job API、狀態欄位，以及供 Phase 8 Scheduler 使用的 `resource_requirement_json`。

## 已完成項目

- 建立 `training_jobs` table。
- Training Job 必須綁定 `project_id`、`dataset_version_id`、`base_model_id`、`trainer_id`。
- 建立 Project-scoped API：
  - `POST /projects/{project_id}/training-jobs`
  - `GET /projects/{project_id}/training-jobs`
  - `GET /projects/{project_id}/training-jobs/{training_job_id}`
- 建立第一版狀態集合：`PENDING`、`RESOURCE_CHECKING`、`QUEUED`、`DISPATCHED`、`RUNNING`、`SUCCESS`、`FAILED`、`CANCELLED`。
- 建立 `resource_requirement_json` 與 `training_config_json`，讓 Scheduler / Worker 後續讀取。
- 建立 `assigned_server_id` nullable 欄位，供 Phase 8 Scheduler 派工後填入。
- 建立基本驗證：
  - Project 必須存在。
  - Dataset Version 必須屬於同一個 Project。
  - Dataset Version 必須是 `READY`。
  - Base Model 必須存在。
  - Trainer 必須存在。
- 保持 Web API 只做 CRUD / 狀態查詢，不執行訓練。

## 產生 / 修改的檔案

```
backend/app/models/training_job.py
backend/app/schemas/training_job.py
backend/app/repositories/training_job_repository.py
backend/app/services/training_job_service.py
backend/app/routers/training_jobs.py
backend/app/models/__init__.py
backend/app/main.py
backend/alembic/versions/b7c8d9e0f1a2_create_training_jobs_table.py
backend/tests/test_training_jobs.py
develope-log/phase-7.md
```

## 如何測試

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：`50 passed`，Alembic head 為 `b7c8d9e0f1a2`。

## 下一步

Phase 8：Scheduler / Dispatcher，掃描 `PENDING` / `QUEUED` jobs，檢查 Dataset READY 與 Training Server 資源，完成派工狀態流。
