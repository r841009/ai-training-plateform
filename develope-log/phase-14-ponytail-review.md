# Phase 14 Ponytail Review

日期：2026-07-06

backend/app/schemas/evaluation.py:L34: yagni: `dataset_version_id` adds a third evaluate target not listed in Phase 14. Keep only `evaluation_dataset_id`; default evaluation already uses the model version dataset.
backend/app/schemas/evaluation.py:L37: delete: conflict validator exists only because of the extra direct `dataset_version_id` path. Nothing replaces it after the field is removed.
backend/app/services/evaluation_service.py:L61: shrink: direct `payload.dataset_version_id` branch duplicates dataset targeting. Start with `model_version.dataset_version_id`; only override from `evaluation_dataset_id`.
backend/app/services/evaluation_service.py:L63: delete: `target_name` stores report metadata inside `metrics_json`. The result already records `dataset_version_id` / `evaluation_dataset_id`; metrics can stay as accuracy/precision/recall/f1 only.

net: -12 lines possible

## 修正狀態

- 已移除 evaluate request 的直傳 `dataset_version_id` 分支。
- 已移除因此產生的 conflict validator。
- 已移除 `metrics_json["target"]`。
- 驗證：`backend\.venv\Scripts\python.exe -m pytest backend\tests\test_evaluations.py -q`，2 passed。
