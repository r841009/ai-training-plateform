# Phase 0：專案初始化

日期：2026-07-02

## 目標

monorepo 目錄結構、docker-compose（PostgreSQL + Redis）、README。不寫應用程式碼。

## 已完成項目

- monorepo 目錄結構：`backend/` `frontend/` `worker/` `shared/` `infra/`
- `docker-compose.yml`：postgres:16-alpine + redis:7-alpine，皆已實際啟動驗證通過
- `README.md`（專案總覽、目錄結構、快速開始）
- `.env.example`、`.gitignore`

## 產生的檔案

```
docker-compose.yml  .env.example  .gitignore  README.md
backend/README.md  frontend/README.md  worker/README.md  shared/README.md  infra/README.md
```

## 如何測試

```bash
cp .env.example .env
docker compose up -d
docker compose ps   # postgres + redis 應為 Up
```

實測以 `pg_isready` 和 `redis-cli ping` 確認兩容器正常回應，測完已 `docker compose down -v` 清乾淨、刪除本機 `.env`。

## 已知問題

本機 5432 / 6379 port 已被其他服務占用（與 compose 檔本身無關）。長期啟動前需在 `.env` 改用未占用的 `POSTGRES_PORT` / `REDIS_PORT`，或先停用本機既有的 postgres/redis。

## 下一步

Phase 1：FastAPI 專案骨架、DB connection、migration（Alembic）、common response、config 管理、logging、health check。
