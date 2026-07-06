# Phase 13：Retrain

日期：2026-07-06

## 目標

建立 retrain API，從同一個 Project 內既有 Model Version 建立新的 Training Job，並記錄 parent model version。

## 已完成項目

- 新增 Project-scoped retrain API：

```text
POST /projects/{project_id}/model-versions/{model_version_id}/retrain
```

- Retrain 行為：
  - 只能讀取同一個 Project 底下的 Model Version。
  - 會取得 parent Model Version 對應的 parent Training Job。
  - 新 Training Job 會沿用 parent job 的：
    - `dataset_version_id`
    - `base_model_id`
    - `trainer_id`
    - `resource_requirement_json`
    - `training_config_json`
  - 會移除 resume-only 欄位：
    - `resume`
    - `checkpoint_latest_path`
  - 會在 `training_config_json` 寫入 `parent_model_version_id`。
- Child Training Job 成功後，Phase 12 的 Model Version 建立流程會產生 child Model Version，並寫入 `parent_model_version_id`。

## 產生 / 修改的檔案

```text
backend/app/services/model_version_service.py
backend/app/routers/model_versions.py
backend/tests/test_worker_manager.py
README.md
develope-log/phase-13.md
```

## 如何測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_worker_manager.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：

- `tests/test_worker_manager.py`：`6 passed`
- 全量 backend tests：`67 passed`
- Alembic head：`e3f4a5b6c7d8`

## 已知限制

- Retrain 目前不提供 override payload，先沿用 parent job 設定。
- Training Job 的 parent 記錄目前放在 `training_config_json.parent_model_version_id`，沒有新增獨立欄位。

## 下一步

Phase 14：Evaluation Dataset 與 Evaluation Result。建立 mock evaluation result。
