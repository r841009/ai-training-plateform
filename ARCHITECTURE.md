# Architecture

系統拆成以下 6 個模組。Web API 不可直接執行訓練邏輯。

## 1. Web / Backend API

負責：

- Project 管理
- Dataset Version 管理
- Base Model 查詢
- Training Job 建立 / 狀態查詢
- Model Version 查詢
- Evaluation Result 查詢
- Retrain 操作

Web API 不可以直接執行訓練。

## 2. Scheduler / Dispatcher 派工服務

負責：

- 掃描 pending / queued training jobs
- 檢查 Training Server 資源，判斷是否可以派工
- 若資源足夠，派發給 Training Worker；不足則維持 queued
- 追蹤 job 狀態，處理 interrupted / resumable / failed

### Resource-aware Scheduling

Training Server 需要記錄：

- server_id / hostname / ip / status
- gpu_count / gpu_memory_total / gpu_memory_free / gpu_utilization
- cpu_usage / ram_free / disk_free
- running_job_count / max_concurrent_jobs / last_heartbeat_at

Training Job 需要 resource_requirement_json：

- required_gpu_memory_gb / required_ram_gb / required_disk_gb
- preferred_gpu_count / estimated_training_time / max_concurrent_policy

第一版簡化規則：

```
如果 server.gpu_memory_free >= job.required_gpu_memory_gb
且 server.ram_free >= job.required_ram_gb
且 server.running_job_count < server.max_concurrent_jobs
則可以派工，否則維持 queued。
```

### Trainer Registry

訓練服務要可擴展，不要把 YOLO trainer 寫死在 Scheduler 裡。

trainer_registry 欄位：trainer_id / trainer_name / task_type / base_model_family / entrypoint / docker_image / supported_resume / supported_export_formats / is_active

- 第一版：entrypoint 直接啟動 `python trainers/yolo_train.py --config xxx`
- 未來：`docker run --gpus all aoi-trainer-yolo:latest`
- 再未來：Kubernetes Job

## 3. Resource Monitor

監控 Training Server：

- GPU 型號 / 數量 / memory total / memory free / utilization
- CPU 使用率 / RAM 剩餘量 / Disk 剩餘量
- 目前執行中的 training job 數量
- server heartbeat

## 4. Training Worker Manager

長駐服務，負責：

- 接收 Scheduler 派工，啟動對應的訓練程式
- 監控 process，回報 heartbeat
- 捕捉 stdout / stderr
- 接收 cancel / pause / resume 指令
- 寫入訓練狀態，訓練完成後回報結果

## 5. Training Script

.py 檔案，平常不執行，由 Worker Manager 於需要時啟動。必須支援：

- 讀取 config file、指定 job_id、讀取 dataset manifest
- 執行訓練、定期寫 checkpoint、定期寫 metrics、定期 heartbeat
- 支援 resume from checkpoint、優雅處理 stop signal
- 訓練完成後輸出 model artifact

### Checkpoint / Resume

Checkpoint 至少包含：model weights / optimizer state / scheduler state / epoch / step / best metrics / random seed / training config / dataset version / class mapping

檔案：`checkpoint_latest.pt`、`checkpoint_best.pt`、`checkpoint_epoch_0010.pt` ...

Policy：每 N epoch 或每 N 分鐘存一次、validation 變好時存 best、永遠保留 latest、最多保留最近 N 個。

Resume 流程：

1. Worker 或 Scheduler 發現 job 中斷 → `training_jobs.status = INTERRUPTED`
2. 若存在 `checkpoint_latest.pt` → 標記 `RESUMABLE`
3. 呼叫 `POST /projects/{project_id}/training-jobs/{job_id}/resume`
4. Scheduler 重新檢查資源，Worker 從 `checkpoint_latest.pt` 接續訓練

### Training Job 狀態機

`PENDING → RESOURCE_CHECKING → (QUEUED | DISPATCHED) → RUNNING → SUCCESS`

中斷路徑：`RUNNING → INTERRUPTED → RESUMABLE → RESUMING → RUNNING`

其他狀態：`PAUSING` / `PAUSED` / `FAILED` / `CANCELLED`

## 6. Storage Service

負責：

- 大量影像上傳、zip upload、folder import
- 未來擴展 multipart upload / MinIO / S3
- 儲存 raw dataset、processed dataset、manifest、checkpoint、model files、evaluation reports
