# Phase 1：Backend 基礎架構

日期：2026-07-02

## 目標

FastAPI 專案骨架、DB connection、Alembic migration、common response 格式、config 管理、logging、health check。不含任何 business feature（Project 等資源留到 Phase 2）。

## 已完成項目

- FastAPI app（`app/main.py`），全域 exception handler 統一輸出 `{success, data, error}` 格式
- Config 管理：`app/config.py`，`pydantic-settings` 讀 `.env`，不硬編碼 DB/Redis 連線資訊
- DB connection：`app/db.py`，SQLAlchemy 2.0 + psycopg3，`get_db()` dependency、`ping_db()` 供 health check 用
- Alembic migration：`alembic.ini` + `alembic/env.py`（DB URL 從 `app.config` 讀取，非寫死；`target_metadata` 指向 `app.db.Base`）
- Common response：`app/schemas/response.py`（`ApiResponse[T]` 泛型 + `success_response` / `error_response`）
- Logging：`app/logging_config.py`，stdlib `logging.basicConfig`，level 可由 config 調整
- Health check：`GET /health`，回傳 DB 連線狀態

## 產生的檔案

```
backend/requirements.txt
backend/alembic.ini
backend/alembic/env.py
backend/alembic/script.py.mako
backend/alembic/versions/            (空，尚無 model)
backend/app/__init__.py
backend/app/main.py
backend/app/config.py
backend/app/db.py
backend/app/logging_config.py
backend/app/schemas/__init__.py
backend/app/schemas/response.py
backend/app/routers/__init__.py
backend/app/routers/health.py
backend/tests/test_health.py
```

## 如何測試

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# 另開 docker-compose（見 Phase 0），.env 指向對應的 POSTGRES_*/REDIS_* port
.venv/bin/python -m alembic upgrade head   # 驗證 migration 連得上 DB
.venv/bin/python -m pytest -q              # 2 passed
.venv/bin/uvicorn app.main:app --port 8000
curl localhost:8000/health                 # {"success":true,"data":{"status":"ok","database":"ok"}}
```

已實際跑過以上全部流程（venv 安裝、alembic upgrade head 連線 dockerized Postgres、pytest 2 passed、uvicorn 起服務後 curl `/health` 與未知路徑皆回傳正確的 common response 格式），測完已停掉 uvicorn、`docker compose down -v`、清除本機 `.env`。

## 踩坑記錄

- `psycopg[binary]==3.2.3` 在 Python 3.14 沒有對應 wheel，升到 `3.2.10`
- `app.exception_handler(HTTPException)` 若匯入 `fastapi.HTTPException`，攔不到路由層（無匹配路徑）丟出的 404，因為那是 `starlette.exceptions.HTTPException`（父類別）。改為匯入 `starlette.exceptions.HTTPException` 註冊，才能同時攔到兩者。

## 下一步

Phase 2：`projects` table、Project CRUD API、`project_code`，確保後續所有資源都會綁 `project_id`。
