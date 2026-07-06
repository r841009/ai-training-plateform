# Phase 3 Ponytail Review

日期：2026-07-06

backend/app/routers/base_models.py:L20-L21: shrink: single-use `base_models` variable. Inline `service.list_base_models()` in the response comprehension.
backend/app/routers/base_models.py:L26-L27: shrink: single-use `base_model` variable. Inline `service.get_base_model(...)` in `BaseModelRead.model_validate(...)`.
backend/app/routers/trainers.py:L20-L21: shrink: single-use `trainers` variable. Inline `service.list_trainers()` in the response comprehension.
backend/app/routers/trainers.py:L26-L27: shrink: single-use `trainer` variable. Inline `service.get_trainer(...)` in `TrainerRead.model_validate(...)`.
backend/app/seed.py:L83-L89: shrink: repeated `apache_license(...)` provider/url calls for multiple rows. Define provider license constants once and reuse them in rows.
backend/app/seed.py:L92-L165: shrink: repeated trainer seed dict boilerplate. One `trainer_row(...)` helper with defaults for `task_type`, `docker_image`, `supported_resume`, and common export formats.
backend/app/seed.py:L168-L185: shrink: duplicated seed upsert loops for base models and trainers. One `_upsert_rows(db, model_cls, key, rows)` helper called twice.

net: -48 lines possible.

## 修正紀錄

日期：2026-07-06

- 已 inline `base_models` router 中的單次使用變數。
- 已 inline `trainers` router 中的單次使用變數。
- 已新增 provider license constants，避免多個 catalog row 重複呼叫相同 `apache_license(...)`。
- 已新增 `trainer_row(...)`，集中 trainer seed row 的共同欄位與預設 export formats。
- 已新增 `_upsert_rows(...)`，共用 base model / trainer seed upsert 流程。

驗證：

- `tests/test_catalog.py`：`7 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
