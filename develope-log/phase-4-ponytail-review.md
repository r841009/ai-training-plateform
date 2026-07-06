# Phase 4 Ponytail Review

日期：2026-07-06

backend/app/models/dataset_version.py:L10-L20: delete: unused `DATASET_STATUSES` tuple and comment. Nothing replaces it until status validation imports it.
backend/app/storage.py:L18-L31: shrink: `safe_extract_zip()` returns a file count that no caller uses. Return `None` and delete `file_count`.
backend/app/services/dataset_version_service.py:L68-L83: stdlib: manual temp file lifecycle with `delete=False`, nullable path, and nested cleanup. `tempfile.TemporaryDirectory()` plus `Path.write_bytes()`.
backend/app/routers/dataset_versions.py:L24-L25: shrink: single-use `dataset_version` variable. Inline `DatasetVersionRead.model_validate(service.create_dataset_version(...))`.
backend/app/routers/dataset_versions.py:L30-L31: shrink: single-use `dataset_versions` variable. Inline the service call in the list comprehension.
backend/app/routers/dataset_versions.py:L38-L39: shrink: single-use `dataset_version` variable. Inline `service.get_dataset_version(...)`.
backend/app/routers/dataset_versions.py:L51-L53: shrink: single-use `content` and `dataset_version` variables. Pass `await file.read()` directly into `service.ingest_zip(...)`.

net: -27 lines possible.

## 修正紀錄

日期：2026-07-06

- 已移除未使用的 `DATASET_STATUSES` tuple 與註解。
- 已讓 `safe_extract_zip()` 改為不回傳未使用的檔案數，刪除 `file_count`。
- 已把 zip ingest 暫存檔流程改成 `tempfile.TemporaryDirectory()` 搭配 `Path.write_bytes()`，移除手動 unlink cleanup。
- 已 inline dataset version router 中 Phase 4 API 的單次使用變數。

驗證：

- `tests/test_dataset_versions.py tests/test_manifest_schemas.py`：`9 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
