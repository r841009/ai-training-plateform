# Phase 7 Ponytail Review

日期：2026-07-06

backend/app/models/training_job.py:L11-L20: delete: unused `TRAINING_JOB_STATUSES` tuple. Nothing replaces it until status validation actually imports it.
backend/app/services/training_job_service.py:L23-L27: shrink: `_require_project()` returns project but all callers discard it. Drop the return value.
backend/app/services/training_job_service.py:L66-L75: shrink: single-use `training_job` variable. `return self.repo.create(TrainingJob(...))`.
backend/tests/test_training_jobs.py:L36-L41: delete: `_yolo_catalog_ids()` helper used by one test. Inline those two lookups in `test_create_training_job_blocks_restricted_yolo_model`.
backend/app/routers/training_jobs.py:L11-L41: Lean already. Ship.
backend/app/schemas/training_job.py:L7-L27: Lean already. Ship.

net: -16 lines possible.

## 修正紀錄

日期：2026-07-06

- 已移除未使用的 `TRAINING_JOB_STATUSES` tuple。
- 已讓 `_require_project()` 只做存在性檢查，不再回傳未使用的 project。
- 已移除 `create_training_job()` 裡單次使用的 `training_job` 變數，直接 `return self.repo.create(TrainingJob(...))`。
- 已移除測試中只用一次的 `_yolo_catalog_ids()` helper，改在該測試內 inline catalog lookup。

驗證：

- `tests/test_training_jobs.py`：`8 passed`
- `tests/test_scheduler.py`：`4 passed`
- `tests/test_worker_manager.py`：`2 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
