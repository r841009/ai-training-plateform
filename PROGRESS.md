請依照以下階段循序完成。每個 Phase 完成後即停下回報（規則見 CLAUDE.md），等待確認再進行下一階段。

## Phase 0：專案初始化

目標：

- 建立 monorepo
- 建立 backend / frontend / worker / shared / infra 結構
- 建立 Docker Compose
- 建立 PostgreSQL
- 建立 Redis 或 RabbitMQ
- 建立基本 README

## Phase 1：Backend 基礎架構

目標：

- 建立 FastAPI 專案
- 建立 DB connection
- 建立 migration 工具
- 建立 common response
- 建立 config 管理
- 建立 logging
- 建立 health check

## Phase 2：Project 模組

目標：

- 建立 projects table
- 建立 Project CRUD API
- 建立 project_code
- 確保後續所有資源都會綁 project_id

## Phase 3：Base Model 與 Trainer Registry

目標：

- 建立 base_models table
- 建立 trainer_registry table
- 建立 seed data
- 建立 Base Model 查詢 API
- 建立 Trainer 查詢 API

## Phase 4：Dataset Version 模組

目標：

- 建立 dataset_versions table
- 建立 Dataset Version CRUD
- 建立 zip upload 或 folder import 的第一版接口
- 建立 dataset status flow
- 建立 dataset manifest 格式
- 建立 dataset validation report 格式

## Phase 5：Dataset Processing Service

目標：

- 實作 dataset validation
- 檢查圖片是否可讀
- 檢查 label 是否存在
- 檢查 label 格式
- 建立 train / val / test split
- 產生 dataset_manifest.jsonl
- 產生 class_mapping.json
- 產生 dataset_statistics.json
- 將 Dataset Version 狀態更新為 READY

## Phase 6：Training Server Resource Monitor

目標：

- 建立 training_servers table
- 建立 resource heartbeat API
- 建立 Training Server 註冊機制
- 建立 GPU / CPU / RAM / Disk resource schema
- 第一版可以先 mock resource，再保留實際 nvidia-smi 擴充

## Phase 7：Training Job 模組

目標：

- 建立 training_jobs table
- 建立 Training Job API
- 支援 PENDING / QUEUED / RUNNING / SUCCESS / FAILED 等狀態
- Training Job 必須綁 project_id、dataset_version_id、base_model_id、trainer_id
- 建立 resource_requirement_json

## Phase 8：Scheduler / Dispatcher

目標：

- 建立 Scheduler service
- 掃描 PENDING / QUEUED jobs
- 檢查 dataset 是否 READY
- 檢查 server resource 是否足夠
- 若足夠則 assigned_server_id 並改為 DISPATCHED
- 若不足則改為 QUEUED
- 不要真的訓練，先完成派工狀態流

## Phase 9：Worker Manager

目標：

- 建立 worker_manager.py
- Worker Manager 可以取得 DISPATCHED job
- 啟動 mock trainer
- 回報 heartbeat
- 更新 job status 為 RUNNING / SUCCESS / FAILED
- 捕捉 log

## Phase 10：Training Script 第一版

目標：

- 建立 trainers/yolo_train.py 或 mock_train.py
- 支援讀取 training_config.json
- 支援 job_id
- 支援 dataset_manifest.jsonl
- 支援 metrics.jsonl
- 支援 checkpoint_latest.pt
- 支援 checkpoint_best.pt
- 支援 resume flag
- 第一版可以先用 mock training loop 模擬 epoch，不一定要真的訓練 YOLO

## Phase 11：Checkpoint / Resume

目標：

- 建立 checkpoints table
- Worker 中斷時標記 INTERRUPTED
- 若 checkpoint_latest 存在，標記 RESUMABLE
- 建立 resume API
- Scheduler 可重新派工 resumable job
- Worker 可從 checkpoint_latest 接續

## Phase 12：Model Version 模組

目標：

- 建立 model_versions table
- 訓練成功後產生 Model Version
- Model Version 必須 project-scoped
- 命名格式為 {project_code}{base_model}{YYYYMMDD_HHmmss}
- 支援 version_no
- 支援 parent_model_version_id
- 不允許 retrain 覆蓋舊模型

## Phase 13：Retrain

目標：

- 建立 retrain API
- 只允許同 Project 內的 Model Version 被 retrain
- Retrain 建立新的 Training Job
- Training Job 記錄 parent_model_version_id
- 成功後產生新的 Model Version

## Phase 14：Evaluation Dataset 與 Evaluation Result

目標：

- 建立 evaluation_datasets table
- 建立 evaluation_results table
- 支援 Project-scoped evaluation dataset
- 支援 model_version 對 test set / external evaluation dataset 評估
- 第一版可先 mock evaluation result
- 保留未來真實推論與 metrics 計算擴充

## Phase 15：Frontend

目標：

- 建立 Vue 3 + Element Plus
- 建立 Project List
- 建立 Project Detail
- Project Detail 內包含：
  - Overview
  - Dataset Versions
  - Training Jobs
  - Model Versions
  - Evaluation Results
  - Retrain
- Model Versions 必須只顯示目前 Project 的模型
- 不要做全平台混合 Model Versions 頁面

實作狀態：

- 已建立 `frontend/index.html`，使用 Vue 3 + Element Plus CDN，免 Node build
- 已建立 Project List / Project Detail
- Project Detail 已包含 Overview、Dataset Versions、Training Jobs、Model Versions、Evaluation Results、Retrain 操作
- Backend 已加入 localhost CORS，支援本機前端呼叫 API

## Phase 16：整合測試

目標：

- 建立一個 Project
- 匯入 Dataset
- 建立 Training Job
- Scheduler 派工
- Worker 執行 mock training
- 產生 checkpoint
- 成功產生 Model Version
- 執行 mock evaluation
- 執行 retrain
- 確認 retrain 產生新的 Model Version
- 確認不同 Project 的 Model Versions 不會互相顯示

完成後提供完整測試流程。
