# Phase 4：Dataset Version 模組

日期：2026-07-02

## 目標

`dataset_versions` table、Dataset Version CRUD、zip upload 第一版接口、dataset status flow、dataset manifest 格式、dataset validation report 格式。

## 已完成項目

- `dataset_versions` table：`project_id`(FK) / `version_no`（per-project 自動遞增，`(project_id, version_no)` unique）/ `status` / `storage_path` / `description`
- Dataset Version CRUD，全部 project-scoped：`POST/GET /projects/{project_id}/datasets`、`GET /projects/{project_id}/datasets/{id}`——跨 project 存取一律 404（已測試）
- Zip upload：`POST /projects/{project_id}/datasets/{id}/upload`，解壓縮到 [DATASET.md](../DATASET.md) 定義的 `raw/` 目錄，狀態依文件流程走 `CREATED/UPLOADED → UPLOADING → UPLOADED`；解壓失敗（壞檔、zip-slip 路徑跳脫）狀態會退回原本的值並回 422，不會卡在 `UPLOADING`
- Zip-slip 防護：`app/storage.py` 的 `safe_extract_zip` 逐一檢查每個 zip entry 解壓後路徑是否還在目的目錄底下，是常見的 zip 上傳安全漏洞（OWASP 路徑穿越類）
- Storage 路徑依 [DATASET.md](../DATASET.md) 規格：`{storage_root}/projects/{project_code}/datasets/v{version_no}/`，建立時就先把 `raw/processed/splits/manifests/validation` 五個子目錄建好
- Dataset manifest / validation report 格式：`app/schemas/manifest.py` 定義 `DatasetManifestEntry`（對應 dataset_manifest.jsonl 每行）與 `DatasetValidationReport`/`InvalidFileEntry`（對應 validation_report.json / invalid_files.json），只定義格式，實際產生邏輯留給 Phase 5

## 產生 / 修改的檔案

```
backend/app/storage.py
backend/app/models/dataset_version.py
backend/app/models/__init__.py
backend/app/schemas/dataset_version.py
backend/app/schemas/manifest.py
backend/app/repositories/dataset_version_repository.py
backend/app/services/dataset_version_service.py
backend/app/routers/dataset_versions.py
backend/app/main.py                     (掛上 dataset_versions router)
backend/app/config.py                   (加 storage_root)
backend/requirements.txt                (加 python-multipart，upload 需要)
backend/alembic/versions/02cee7ccc202_create_dataset_versions_table.py
backend/tests/conftest.py               (STORAGE_ROOT 指向測試暫存目錄)
backend/tests/test_dataset_versions.py
backend/tests/test_manifest_schemas.py
```

## 如何測試

```bash
cd backend
.venv/bin/python -m pytest -q        # 21 passed，SQLite in-memory

# 對真的 Postgres + 真實檔案：
.venv/bin/python -m alembic upgrade head
.venv/bin/uvicorn app.main:app --port 8001
curl -X POST localhost:8001/projects -d '{"project_code":"LED_SCRATCH","name":"LED Scratch"}'
curl -X POST localhost:8001/projects/{project_id}/datasets -d '{}'
curl -X POST localhost:8001/projects/{project_id}/datasets/{dataset_version_id}/upload -F "file=@sample.zip"
```

已實測：pytest 21 passed；對 dockerized Postgres 跑 migration 建表；起真實服務，建立 project → dataset version → 用真的 zip 檔（含 images/a.jpg、labels/a.txt）上傳，status 從 `CREATED` 變成 `UPLOADED`，並且用 `find` 確認檔案真的解壓到 `storage_dev/projects/LED_SCRATCH/datasets/v1/raw/{images,labels}/` 底下，目錄結構完全符合 DATASET.md 規格。測完已清乾淨（停服務、`docker compose down -v`、刪 `.env`、刪測試用的 storage 目錄）。

## 已知限制

- `version_no` 用 `max(version_no)+1` 配前一步查詢再寫入，高並發下同一個 project 同時建立多筆可能撞號（有 unique constraint 保底不會寫入錯誤資料，但會回 500 而不是自動重試）。目前平台使用情境不會有這種併發，先不處理。

## 下一步

Phase 5：Dataset Processing Service——實作圖片可讀性檢查、label 存在性/格式檢查、產生 train/val/test split、產生 dataset_manifest.jsonl / class_mapping.json / dataset_statistics.json，並把狀態推進到 `READY`。
