# Phase 5 Ponytail Review

日期：2026-07-06

backend/app/services/dataset_version_service.py:L16: yagni: `PROCESSABLE_STATUSES = {"UPLOADED"}` is a one-value set. `dataset_version.status != "UPLOADED"`.
backend/app/services/dataset_version_service.py:L36-L43: shrink: single-use `dataset_version` variable. `return self.repo.create(DatasetVersion(...))`.
backend/app/dataset_processing.py:L137-L146 and L188-L198: shrink: repeated `DatasetValidationReport(...)` construction. One small `_build_validation_report(...)` helper.
backend/app/dataset_processing.py:L172-L176: shrink: manual split grouping loop. Dict comprehension over `("train", "val", "test")`.
backend/app/dataset_processing.py:L178-L186: shrink: single-use `statistics` variable. Inline into `write_text(json.dumps(...))`.
backend/tests/test_dataset_process_api.py:L8-L19: shrink: `_real_jpeg_bytes()` + `_make_zip()` duplicate helpers seen across dataset/training tests. Move to one local test helper module only if another phase touches them again.
backend/app/dataset_processing.py:L58-L68: Lean already. Ship.

net: -20 lines possible.

## 修正紀錄

日期：2026-07-06

- 已移除單值 `PROCESSABLE_STATUSES`，改用 `dataset_version.status != "UPLOADED"`。
- 已移除 `create_dataset_version()` 裡單次使用的 `dataset_version` 變數，直接 `return self.repo.create(DatasetVersion(...))`。
- 已新增 `_build_validation_report()`，集中 `DatasetValidationReport` 建構邏輯。
- 暫時保留 split grouping loop，因為目前比壓成 comprehension 更直觀。
- 暫時保留 `statistics` 單次變數，避免把大型 dict 塞進 `write_text()` 降低可讀性。
- 暫時不抽共用 test zip/image helper，等更多 phase 測試重複時再整理。

驗證：

- `tests/test_dataset_processing.py`：`11 passed`
- `tests/test_dataset_process_api.py`：`5 passed`
- `tests/test_training_jobs.py tests/test_scheduler.py tests/test_worker_manager.py`：`14 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
