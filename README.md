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
- `develope-log/` — 各階段完成紀錄與測試結果

## 快速開始

```bash
cp .env.example .env
docker compose up -d
```

啟動 PostgreSQL（5432）與 Redis（6379）。若本機 port 已被占用，可在 `.env` 調整 `POSTGRES_PORT` / `REDIS_PORT`。

## 目前進度

目前已完成到 **Phase 15：Frontend**，並完成一項緊急的模型授權安全修正。

已完成：

- Phase 0：monorepo、Docker Compose、PostgreSQL、Redis、基本文件
- Phase 1：FastAPI backend、config、DB connection、Alembic、logging、health check、common response
- Phase 2：Project CRUD
- Phase 3：Base Model 與 Trainer Registry
- Phase 4：Dataset Version CRUD、zip upload、storage layout、manifest/report schema
- Phase 5：Dataset Processing Service，支援圖片/label validation、train/val/test split、manifest/statistics 產生
- Phase 6：Training Server Resource Monitor，支援 server 註冊與 resource heartbeat
- Phase 7：Project-scoped Training Job API，支援 `resource_requirement_json`
- Phase 8：Scheduler / Dispatcher，可掃描 `PENDING` / `QUEUED` jobs，依 Dataset READY 狀態與 Training Server 資源進行 `DISPATCHED` / `QUEUED` / `FAILED` 狀態流
- Phase 9：Worker Manager，可取得 `DISPATCHED` jobs，執行 mock trainer，回報 heartbeat，更新 `RUNNING` / `SUCCESS` / `FAILED`，並在 Project-scoped storage 路徑捕捉 worker log
- Phase 10：Training Script 第一版，`trainers/mock_train.py` 可讀取 config / manifest，輸出 `metrics.jsonl` 與 latest/best checkpoints
- Phase 11：Checkpoint / Resume，支援 `checkpoints` table、resume API、`RESUMABLE` jobs 重新派工，以及 Worker 中斷後 checkpoint 偵測
- Phase 12：Model Version 模組，訓練成功後產生 Project-scoped Model Version，支援 `version_no` 與 `parent_model_version_id`
- Phase 13：Retrain，可從同一 Project 內既有 Model Version 建立 child Training Job，並在成功後產生 child Model Version
- Phase 14：Evaluation Dataset 與 Evaluation Result，支援 Project-scoped evaluation dataset 與 mock evaluation result
- Phase 15：Vue 3 + Element Plus 前端操作台，支援 Project List / Project Detail、Dataset、Training Job、Model Version、Evaluation、Retrain
- 緊急授權安全修正：Base Model 目錄已加入授權欄位，YOLO 系列預設封鎖 OEM/proprietary training，並加入較適合商用評估的替代 detection model catalog

下一步：

- Phase 16：整合測試，串起 Project / Dataset / Training / Worker / Model / Evaluation / Retrain 流程

## Frontend

```powershell
# terminal 1: backend API
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# terminal 2: frontend static app
cd ..
python -m http.server 5173 --directory frontend
```

開啟 `http://127.0.0.1:5173?mock=1`。前端預設使用 standalone mock API，不需要 PostgreSQL / Redis / backend。

如需切換到真實 API，可在瀏覽器 console 設定：

```js
localStorage.setItem('apiBase', 'http://127.0.0.1:8000')
```

切回 standalone mock：

```js
localStorage.setItem('apiBase', 'mock')
```

## Backend 測試

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m alembic heads
```

目前最近一次實測結果：

- `69 passed`
- Alembic head：`f4a5b6c7d8e9`

## Worker Manager 第一版

```powershell
# 需先讓 Scheduler 將 job 派成 DISPATCHED，並填入 assigned_server_id
$env:PYTHONPATH = ".\backend"
.\backend\.venv\Scripts\python.exe -m worker.worker_manager <training_server_id>
```

## Training Script 第一版

```powershell
.\backend\.venv\Scripts\python.exe -m trainers.mock_train `
  --config training_config.json `
  --job-id <training_job_id> `
  --manifest dataset_manifest.jsonl `
  --output-dir <job_output_dir> `
  --resume
```

## 目前主要 API

- `GET /health`
- `POST /projects`
- `GET /projects`
- `GET /projects/{project_id}`
- `PATCH /projects/{project_id}`
- `DELETE /projects/{project_id}`
- `GET /base-models`
- `GET /trainers`
- `POST /projects/{project_id}/datasets`
- `GET /projects/{project_id}/datasets`
- `POST /projects/{project_id}/datasets/{dataset_version_id}/upload`
- `POST /projects/{project_id}/datasets/{dataset_version_id}/process`
- `POST /training-servers`
- `GET /training-servers`
- `POST /training-servers/{training_server_id}/heartbeat`
- `POST /projects/{project_id}/training-jobs`
- `GET /projects/{project_id}/training-jobs`
- `POST /projects/{project_id}/training-jobs/{training_job_id}/resume`
- `GET /projects/{project_id}/model-versions`
- `GET /projects/{project_id}/model-versions/{model_version_id}`
- `POST /projects/{project_id}/model-versions/{model_version_id}/retrain`
- `POST /projects/{project_id}/model-versions/{model_version_id}/evaluate`
- `POST /projects/{project_id}/evaluation-datasets`
- `GET /projects/{project_id}/evaluation-datasets`
- `GET /projects/{project_id}/evaluation-results`
- `POST /scheduler/dispatch-once`

## 模型授權安全狀態

Base Model catalog 已記錄 `source_provider`、`license_name`、`license_url`、`license_risk_level`、`commercial_use_allowed`、`oem_use_allowed`、`requires_enterprise_license`、`license_notes`。

目前策略：

- Ultralytics YOLOv8 / YOLOv11 標為高風險，預設不可用於 OEM / proprietary training；若需使用，必須先確認 Enterprise License 覆蓋該專案與部署方式。
- 新增商用較友善的替代 detection model catalog，例如 torchvision detection、YOLOX、Detectron2、DETR、PaddleDetection、MMDetection 相關候選。
- Training Job 建立時會阻擋未核准 OEM 或需要 enterprise license 的 Base Model。

授權風險控管是工程防線，不等同法律意見；正式量產或客戶交付前仍需確認實際使用的 code、weights、pretrained checkpoints 與部署方式。
