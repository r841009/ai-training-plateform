# Phase 2：Project 模組

日期：2026-07-02

## 目標

`projects` table、Project CRUD API、`project_code`，確保後續所有資源都會綁 `project_id`。

## 已完成項目

- `projects` table：`id`(UUID) / `project_code`(unique) / `name` / `description` / `created_at` / `updated_at`
- `project_code` 規則：僅允許大寫英數字與底線（`^[A-Z0-9_]+$`），因為會直接用於 storage 路徑與 Model Version 命名，建立後不可修改（`ProjectUpdate` 不含這個欄位）
- Project CRUD：`POST /projects`、`GET /projects`、`GET /projects/{id}`、`PATCH /projects/{id}`、`DELETE /projects/{id}`，皆走 router → service → repository 分層
- `project_code` 重複建立回 409；找不到的 project 回 404；格式不符回 422 —— 全部走 Phase 1 的 common response envelope
- 新增 `GUID` type（`app/types.py`）：Postgres 用原生 UUID，其他 dialect（測試用 SQLite）退化成 CHAR(36)，讓 CRUD 測試不需要真的 Postgres 就能跑

## 產生 / 修改的檔案

```
backend/app/types.py
backend/app/models/__init__.py
backend/app/models/project.py
backend/app/schemas/project.py
backend/app/repositories/__init__.py
backend/app/repositories/project_repository.py
backend/app/services/__init__.py
backend/app/services/project_service.py
backend/app/routers/projects.py
backend/app/main.py                          (掛上 projects router)
backend/alembic/env.py                       (import app.models 讓 autogenerate 抓得到 table)
backend/alembic/versions/4803da49de22_create_projects_table.py
backend/tests/conftest.py                     (SQLite in-memory fixture)
backend/tests/test_projects.py
```

## 如何測試

```bash
cd backend
.venv/bin/python -m pytest -q        # 7 passed，用 SQLite in-memory，不需要 Docker

# 對真的 Postgres 驗證 migration + API
.venv/bin/python -m alembic upgrade head
.venv/bin/uvicorn app.main:app --port 8001
curl -X POST localhost:8001/projects -d '{"project_code":"LED_SCRATCH","name":"LED Scratch Detection"}'
curl localhost:8001/projects
```

已實測：pytest 7 passed；`alembic upgrade head` 對 dockerized Postgres 建出 `projects` table；起真的 uvicorn 後對 `/projects` 做 create / duplicate(409) / list / invalid(422) 全部行為正確。測完已停服務、`docker compose down -v`、清除 `.env`。

## 踩坑記錄

- Autogenerate 產生的 migration 用到自訂型別 `app.types.GUID()`，但沒有自動加 `import app.types`，每次對這個型別跑 autogenerate 都要手動補這行 import（Alembic 對自訂型別的已知限制，非 bug）
- 本機同時有其他服務用 Docker 佔用 8000 port（IPv6 wildcard），curl 預設先打 IPv6 導致打到別的服務，改用 8001 才測到自己的 API — 之後在此機器上測試 backend 建議固定用非常見 port（例如 8001）

## 下一步

Phase 3：`base_models` table、`trainer_registry` table、seed data、Base Model 查詢 API、Trainer 查詢 API。
