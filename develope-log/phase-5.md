# Phase 5：Dataset Processing Service

日期：2026-07-02

## 目標

實作 dataset validation（圖片可讀性、label 存在性/格式）、產生 train/val/test split、產生 dataset_manifest.jsonl / class_mapping.json / dataset_statistics.json，成功後把 Dataset Version 狀態推進到 `READY`。

## 已完成項目

- `app/dataset_processing.py`：純函式模組，不碰 DB，方便單元測試
  - `validate_image()`：用 Pillow 開圖 + `verify()` 確認可讀
  - `parse_yolo_label()`：解析 YOLO 格式 label（`class_id cx cy w h`，5 欄、數值需在 `[0,1]`）；label 檔不存在視為無效，但**空檔案**視為合法的「無物件」負樣本
  - `assign_splits()`：均勻隨機切分（fixed seed），標註為 ponytail 簡化——之後如果 class 分佈不均需要 stratified split 再加
  - `validate_dataset()` / `finalize_dataset()` / `write_invalid_report()`：組出完整流程，產生 DATASET.md 規格的全部輸出檔案
- 新 API：`POST /projects/{project_id}/datasets/{id}/process`，只有 `UPLOADED` 狀態才能觸發（409 擋掉其他狀態，包含重複呼叫）
- 狀態機依 DATASET.md 走：`UPLOADED → VALIDATING →`（沒有任何有效圖片 → `INVALID`；否則 `→ PROCESSING → READY`）
- Class distribution 統計、split 比例可由 request body 調整（`train_ratio`/`val_ratio`/`test_ratio`，必須加總為 1，否則 422）；可選 `class_names` 覆寫預設的 `class_{id}` 命名

## 產生 / 修改的檔案

```
backend/app/dataset_processing.py
backend/app/schemas/dataset_version.py         (加 DatasetProcessRequest)
backend/app/services/dataset_version_service.py (加 process_dataset)
backend/app/routers/dataset_versions.py        (加 /process endpoint)
backend/requirements.txt                       (加 Pillow)
backend/tests/test_dataset_processing.py        (純函式單元測試)
backend/tests/test_dataset_process_api.py       (API 整合測試)
```

## 如何測試

```bash
cd backend
.venv/bin/python -m pytest -q        # 37 passed

# 對真的服務 + 真實圖片：
.venv/bin/uvicorn app.main:app --port 8001
# 建 project → dataset version → 上傳含 10 張正常圖 + 1 張壞圖的 zip → POST .../process
```

已實測：pytest 37 passed；對 dockerized Postgres + 真實服務，上傳一個含 10 張正常 JPEG（3 個 class 輪流）+ 1 張刻意損壞的「假圖片」的 zip，呼叫 `/process` 後：
- status `UPLOADED → READY`
- `dataset_statistics.json`：`valid_files=10, invalid_files=1`，split 7/2/1（對應 70/20/10）
- `class_mapping.json` 產生 3 個 class
- `invalid_files.json` 正確抓出壞圖並附上原因
- `dataset_manifest.jsonl` 剛好 10 行

測完已清乾淨（停服務、`docker compose down -v`、刪 `.env`、刪 storage 測試目錄）。

## 已知限制

- Split 目前是均勻隨機（fixed seed），DATASET.md 提到的 stratified split（依 class 分佈）先不做，等真的遇到 class 不平衡問題再加
- Dataset 必須遵循 `raw/images/` + `raw/labels/`（鏡像子目錄結構）的慣例，不支援任意檔案佈局；不符合此結構會直接判定 0 張有效圖片 → `INVALID`

## 下一步

Phase 6：Training Server Resource Monitor——`training_servers` table、resource heartbeat API、GPU/CPU/RAM/Disk resource schema，第一版先 mock resource。
