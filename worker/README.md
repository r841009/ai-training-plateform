Training Worker Manager + Training Script（trainers/）。接收 Scheduler 派工、執行訓練、checkpoint/resume。見 [Architecture #4-5](../ARCHITECTURE.md#4-training-worker-manager)。

## Phase 9 狀態

已建立第一版 `worker_manager.py`：

- 取得指定 Training Server 的 `DISPATCHED` jobs
- 將 job 更新為 `RUNNING`
- 執行內建 `MockTrainerRunner`
- 成功時更新為 `SUCCESS`
- 失敗時更新為 `FAILED` 並寫入 `failure_reason`
- 更新 Training Server heartbeat
- 完成後釋放 `running_job_count`
- 將 worker log 寫入 Project-scoped storage path

執行方式：

```powershell
$env:PYTHONPATH = ".\backend"
.\backend\.venv\Scripts\python.exe -m worker.worker_manager <training_server_id>
```

## Phase 10 狀態

已建立 `trainers/mock_train.py`：

- 讀取 `training_config.json`
- 讀取 `dataset_manifest.jsonl`
- 支援 `--job-id`
- 輸出 `metrics.jsonl`
- 輸出 `checkpoint_latest.pt` / `checkpoint_best.pt`
- 支援 `--resume` 從 latest checkpoint 下一個 epoch 接續

執行方式：

```powershell
.\backend\.venv\Scripts\python.exe -m trainers.mock_train `
  --config training_config.json `
  --job-id <training_job_id> `
  --manifest dataset_manifest.jsonl `
  --output-dir <job_output_dir> `
  [--resume]
```

## Phase 11 狀態

Worker Manager 目前支援中斷後 resume 的最小狀態流：

- 捕捉 `KeyboardInterrupt`
- 若 job 目錄存在 `checkpoint_latest.pt`，job 會標記為 `RESUMABLE`
- 寫入一筆 checkpoint row
- resume API 會把 `resume: true` 寫入 `training_config_json`
- Scheduler 可重新派工 `RESUMABLE` job

## Phase 12 狀態

Worker 成功完成 job 後會建立 Model Version：

- 寫出 mock `model_artifact.json`
- 建立 Project-scoped Model Version
- 版本號使用 Project 內遞增 `version_no`
- 名稱格式：`{project_code}_{base_model}_{YYYYMMDD_HHmmss}`
