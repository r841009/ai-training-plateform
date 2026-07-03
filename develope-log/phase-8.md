# Phase 8：Scheduler / Dispatcher

日期：2026-07-03

## 目標

建立 Scheduler / Dispatcher 第一版，掃描 `PENDING` / `QUEUED` Training Jobs，檢查 Dataset 狀態與 Training Server 資源，完成派工狀態流。不啟動訓練、不呼叫 Worker。

## 已完成項目

- 建立 `SchedulerService`。
- 建立 `POST /scheduler/dispatch-once`，可手動觸發一次派工掃描。
- 掃描 `PENDING` / `QUEUED` jobs。
- 檢查 Dataset Version 是否仍為 `READY`。
- 檢查 Training Server 是否 `ONLINE` 且資源足夠。
- 資源足夠時：
  - 設定 `training_jobs.assigned_server_id`
  - 將 job 狀態改為 `DISPATCHED`
  - 增加 server `running_job_count`
- 資源不足時將 job 狀態改為 `QUEUED`。
- Dataset 不可用時將 job 狀態改為 `FAILED` 並記錄 `failure_reason`。
- 第一版資源判斷使用 `resource_requirement_json`：
  - `required_gpu_memory_gb`
  - `required_ram_gb`
  - `required_disk_gb`
  - `preferred_gpu_count`

## 產生 / 修改的檔案

```
backend/app/repositories/training_job_repository.py
backend/app/repositories/training_server_repository.py
backend/app/schemas/scheduler.py
backend/app/services/scheduler_service.py
backend/app/routers/scheduler.py
backend/app/main.py
backend/tests/test_scheduler.py
develope-log/phase-8.md
```

## 如何測試

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：`54 passed`，Alembic head 維持 `b7c8d9e0f1a2`。

## 下一步

Phase 9：Worker Manager，取得 `DISPATCHED` job，啟動 mock trainer，回報 heartbeat，更新 job status。
