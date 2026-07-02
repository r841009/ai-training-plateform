# AOI AI Training Platform

AOI 缺陷檢測用 AI 訓練平台。Project-scoped 的 Dataset / Training Job / Model Version 管理，支援資源感知派工與 checkpoint/resume。

## 目錄結構

- `backend/` — FastAPI Web API（Project、Dataset、Training Job、Model Version CRUD，不執行訓練）
- `frontend/` — Vue 3 + Element Plus
- `worker/` — Training Worker Manager + Training Script（實際執行訓練的地方）
- `shared/` — backend 與 worker 共用的型別、schema
- `infra/` — migration、部署相關設定

## 文件

- [CLAUDE.md](CLAUDE.md) — 專案規則、目標、技術選型
- [ARCHITECTURE.md](ARCHITECTURE.md) — 模組架構（Scheduler、Resource Monitor、Worker Manager...）
- [DATASET.md](DATASET.md) — Dataset 設計、資料表關聯
- [PROGRESS.md](PROGRESS.md) — 開發階段（Phase 0~16）

## 快速開始

```bash
cp .env.example .env
docker compose up -d
```

啟動 PostgreSQL（5432）與 Redis（6379）。目前僅有基礎設施容器，backend/frontend/worker 尚未實作（見 PROGRESS.md Phase 1 起）。
