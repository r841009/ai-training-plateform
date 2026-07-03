# Phase 6：Training Server Resource Monitor

日期：2026-07-03

## 目標

建立 Training Server Resource Monitor 第一版：`training_servers` table、Training Server 註冊機制、resource heartbeat API、GPU / CPU / RAM / Disk resource schema。第一版由 API 接收 mock/manual heartbeat，不直接整合 `nvidia-smi`。

## 已完成項目

- 建立 `training_servers` table。
- 建立 Training Server 註冊 API：`POST /training-servers`。
- 建立 Training Server 查詢 API：`GET /training-servers`、`GET /training-servers/{training_server_id}`。
- 建立 resource heartbeat API：`POST /training-servers/{training_server_id}/heartbeat`。
- Heartbeat 支援 GPU count / GPU memory total/free / GPU utilization / CPU usage / RAM total/free / disk free / running job count / max concurrent jobs。
- Server status 第一版支援：`REGISTERED`、`ONLINE`、`OFFLINE`、`DRAINING`、`UNAVAILABLE`。
- 保留未來由 Resource Monitor agent 或 Worker Manager 上報真實 `nvidia-smi` 指標的擴充空間。

## 產生 / 修改的檔案

```
backend/app/models/training_server.py
backend/app/schemas/training_server.py
backend/app/repositories/training_server_repository.py
backend/app/services/training_server_service.py
backend/app/routers/training_servers.py
backend/app/models/__init__.py
backend/app/main.py
backend/alembic/versions/9f1a2b3c4d5e_create_training_servers_table.py
backend/tests/test_training_servers.py
develope-log/phase-6.md
```

## 如何測試

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

實測結果：`44 passed`。

## 下一步

Phase 7：Training Job 模組，建立 `training_jobs` table 與 Project-scoped Training Job API。
