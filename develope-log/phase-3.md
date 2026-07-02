# Phase 3：Base Model 與 Trainer Registry

日期：2026-07-02

## 目標

`base_models` table、`trainer_registry` table、seed data、Base Model / Trainer 查詢 API。

## 已完成項目

- `base_models` table：`name`(unique) / `family` / `task_type` / `is_active`。SQLAlchemy 類別命名為 `BaseModelEntry`（避免跟 pydantic 的 `BaseModel` 撞名）
- `trainer_registry` table：對應 [ARCHITECTURE.md](../ARCHITECTURE.md#trainer-registry) 定義的欄位，`supported_export_formats` 用 JSON 存 list（不用逗號字串手動解析）
- 這兩個 API 是**平台層級**，不綁 `project_id`（`GET /base-models`、`GET /trainers`），因為 Base Model / Trainer 是全平台共用的目錄，符合 CLAUDE.md 的 API 設計原則
- Seed data：`app/seed.py`，`seed(db)` 用 unique name 判斷是否已存在，重複執行不會產生重複資料（已實測）
  - Base Model：yolov8n / yolov8s / yolov11n / resnet50 / efficientnet / unet（CLAUDE.md 指定清單）
  - Trainer：`yolo_trainer`（entrypoint: `python trainers/yolo_train.py`）、`mock_trainer`（entrypoint: `python trainers/mock_train.py`，供 Phase 9-10 mock 訓練用）
- `tests/conftest.py` 的 `client` fixture 建立 DB 後會自動呼叫 `seed()`，所有測試都能拿到已知的目錄資料

## 產生 / 修改的檔案

```
backend/app/models/base_model.py
backend/app/models/trainer.py
backend/app/models/__init__.py
backend/app/schemas/base_model.py
backend/app/schemas/trainer.py
backend/app/repositories/base_model_repository.py
backend/app/repositories/trainer_repository.py
backend/app/services/base_model_service.py
backend/app/services/trainer_service.py
backend/app/routers/base_models.py
backend/app/routers/trainers.py
backend/app/main.py                     (掛上兩個 router)
backend/app/seed.py
backend/alembic/versions/74b2529fd35d_create_base_models_and_trainer_registry_.py
backend/tests/conftest.py               (client fixture 自動 seed)
backend/tests/test_catalog.py
```

## 如何測試

```bash
cd backend
.venv/bin/python -m pytest -q                 # 12 passed，SQLite in-memory

# 對真的 Postgres：
.venv/bin/python -m alembic upgrade head
.venv/bin/python -m app.seed                  # 可重複執行，不會重複插入
.venv/bin/uvicorn app.main:app --port 8001
curl localhost:8001/base-models
curl localhost:8001/trainers
```

已實測：pytest 12 passed；對 dockerized Postgres 跑 migration 建表、seed 兩次確認 idempotent（6 個 base model 沒有變成 12 個）、起服務用 curl 打 `/base-models`、`/trainers` 內容正確。測完已清乾淨。

## 下一步

Phase 4：`dataset_versions` table、Dataset Version CRUD、zip upload / folder import 第一版接口、dataset status flow、dataset manifest 格式、dataset validation report 格式。
