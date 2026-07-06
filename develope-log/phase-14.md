# Phase 14：Evaluation Dataset 與 Evaluation Result

日期：2026-07-06

## 目標

建立 evaluation dataset / evaluation result 資料表，支援 Project-scoped evaluation dataset，並可對 Model Version 執行第一版 mock evaluation。

## 已完成項目

- 新增 `evaluation_datasets` table：
  - `project_id`
  - `dataset_version_id`
  - `name`
  - `storage_path`
  - `description`
  - `created_at`
- 新增 `evaluation_results` table：
  - `project_id`
  - `model_version_id`
  - `dataset_version_id`
  - `evaluation_dataset_id`
  - `metrics_json`
  - `report_path`
  - `sample_predictions_path`
  - `created_at`
- 新增 Project-scoped Evaluation Dataset API：

```text
POST /projects/{project_id}/evaluation-datasets
GET /projects/{project_id}/evaluation-datasets
```

- 新增 Evaluation Result API：

```text
GET /projects/{project_id}/evaluation-results
POST /projects/{project_id}/model-versions/{model_version_id}/evaluate
```

- Mock evaluation 會輸出：
  - `evaluation_report.json`
  - `sample_predictions.json`
  - mock metrics：`accuracy` / `precision` / `recall` / `f1`
- 支援兩種 evaluation target：
  - 不傳 payload：使用 Model Version 的 `dataset_version_id`
  - 傳 `evaluation_dataset_id`：使用 Project-scoped external evaluation dataset

## 產生 / 修改的檔案

```text
backend/app/models/evaluation.py
backend/app/repositories/evaluation_repository.py
backend/app/schemas/evaluation.py
backend/app/services/evaluation_service.py
backend/app/routers/evaluations.py
backend/alembic/versions/f4a5b6c7d8e9_create_evaluation_tables.py
backend/app/models/__init__.py
backend/app/main.py
backend/tests/test_evaluations.py
README.md
develope-log/phase-14.md
```

## 如何測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest tests\test_evaluations.py -q
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

實測結果：

- `tests/test_evaluations.py`：`2 passed`
- 全量 backend tests：`69 passed`
- Alembic head：`f4a5b6c7d8e9`

## 已知限制

- Evaluation metrics 目前是 mock 固定值。
- 尚未做真實推論、confusion matrix、sample prediction 內容。
- Frontend 尚未建立，留到 Phase 15。

## 下一步

Phase 15：Frontend。建立 Vue 3 + Element Plus 的 Project / Dataset / Training / Model / Evaluation views。
