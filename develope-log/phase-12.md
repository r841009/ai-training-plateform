# Phase 12：Model Version 模組

日期：2026-07-06

## 目標

建立 `model_versions` table，讓訓練成功後產生 Project-scoped Model Version，支援 `version_no`、`parent_model_version_id` 與不可覆蓋舊模型的資料模型。

## 已完成項目

- 新增 `model_versions` table：
  - `project_id`
  - `training_job_id`
  - `dataset_version_id`
  - `base_model_id`
  - `parent_model_version_id`
  - `version_no`
  - `name`
  - `artifact_path`
  - `metrics_json`
  - `created_at`
- `training_job_id` 設為 unique，避免同一個 training job 重複產生多個 Model Version。
- `(project_id, version_no)` 設為 unique，確保每個 Project 內版本號不重複。
- 新增 Project-scoped Model Version API：

```text
GET /projects/{project_id}/model-versions
GET /projects/{project_id}/model-versions/{model_version_id}
```

- Worker 成功完成 job 後會：
  - 寫出 `model_artifact.json`
  - 建立一筆 Model Version
  - 命名格式：`{project_code}_{base_model}_{YYYYMMDD_HHmmss}`
  - `version_no` 從 Project 內目前最大版本號 + 1
- `parent_model_version_id` 目前可由 `training_config_json.parent_model_version_id` 帶入，且會檢查 parent 必須屬於同一個 Project。

## 產生 / 修改的檔案

```text
backend/app/models/model_version.py
backend/app/repositories/model_version_repository.py
backend/app/schemas/model_version.py
backend/app/services/model_version_service.py
backend/app/routers/model_versions.py
backend/alembic/versions/e3f4a5b6c7d8_create_model_versions_table.py
backend/app/models/__init__.py
backend/app/main.py
backend/tests/test_worker_manager.py
worker/worker_manager.py
README.md
worker/README.md
develope-log/phase-12.md
```

## 如何測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_worker_manager.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：

- `tests/test_worker_manager.py`：`4 passed`
- 全量 backend tests：`65 passed`
- Alembic head：`e3f4a5b6c7d8`

## 已知限制

- Model artifact 目前是 mock `model_artifact.json`，尚未接真實 trainer 輸出的模型檔。
- Worker 仍使用內建 mock runner；尚未改為 subprocess 執行 `trainers.mock_train`。
- Retrain API 尚未建立，留到 Phase 13。

## 下一步

Phase 13：Retrain。建立 retrain API，從既有 Model Version 建立新的 Training Job，並記錄 parent model version。
