# Phase 6 Ponytail Review

日期：2026-07-06

backend/app/services/training_server_service.py:L20-L26: shrink: single-use `training_server` variable. `return self.repo.create(TrainingServer(...))`.
backend/app/services/training_server_service.py:L41-L50: shrink: ten manual heartbeat metric assignments. Loop over metric field names with `setattr(training_server, field, getattr(payload, field))`.
backend/app/routers/training_servers.py:L26-L27: shrink: single-use `training_server` variable. `return success_response(TrainingServerRead.model_validate(service.create_training_server(payload)))`.
backend/app/routers/training_servers.py:L32-L33: shrink: single-use `training_servers` variable. Inline list comprehension over `service.list_training_servers()`.
backend/app/routers/training_servers.py:L40-L41: shrink: single-use `training_server` variable. Inline `service.get_training_server(training_server_id)`.
backend/app/routers/training_servers.py:L50-L51: shrink: single-use `training_server` variable. Inline `service.record_heartbeat(...)`.
backend/app/models/training_server.py:L10-L34: Lean already. Ship.
backend/app/schemas/training_server.py:L9-L56: Lean already. Ship.
backend/app/repositories/training_server_repository.py:L9-L36: Lean already. Ship.

net: -18 lines possible.

## 修正紀錄

日期：2026-07-06

- 已移除 `create_training_server()` 裡單次使用的 `training_server` 變數，直接 `return self.repo.create(TrainingServer(...))`。
- 已新增 `HEARTBEAT_METRIC_FIELDS`，用明確欄位清單集中更新 heartbeat resource metrics。
- 已 inline `training_servers` router 裡單次使用的 `training_server` / `training_servers` 變數。

驗證：

- `tests/test_training_servers.py`：`6 passed`
- `tests/test_scheduler.py`：`4 passed`
- `tests/test_worker_manager.py`：`2 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
