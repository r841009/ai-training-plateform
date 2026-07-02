# Dataset & Data Model

Dataset 必須以 Project 為範圍管理。

## Dataset Version 狀態

`CREATED / UPLOADING / UPLOADED / VALIDATING / INVALID / PROCESSING / READY / ARCHIVED`

只有 `READY` 狀態的 Dataset Version 可以用來訓練。

## 上傳方式

1. 小型資料集 zip upload
2. 大型資料集 folder import
3. 保留 direct multipart upload / MinIO / S3 擴充點

## 儲存結構

```
/storage/projects/{project_code}/datasets/{dataset_version}/
  raw/
  processed/
  splits/
    train.txt
    val.txt
    test.txt
  manifests/
    dataset_manifest.jsonl
    class_mapping.json
    dataset_statistics.json
  validation/
    validation_report.json
    invalid_files.json
```

## Dataset Manifest

每張影像記錄：`image_id / image_path / label_path / split / width / height / class_ids / checksum / metadata`

訓練時讀取 `dataset_manifest.jsonl`，不要每次重新掃資料夾。

## Train / Validation / Test Split

支援三種方式：

1. 自動切分（預設 train 70% / validation 20% / test 10%）
2. 使用者手動指定
3. 匯入既有 train / val / test 結構

保留 stratified split 擴充設計，讓 AOI defect class 在三個集合中維持合理分布。

用途：train 用於更新模型權重，validation 用於訓練中選 best checkpoint，test 用於訓練完成後最終評估。

## Evaluation Dataset

除了 Dataset Version 內建 test set，也支援 External Evaluation Dataset，用途包含：新批次產線圖片、新產品線圖片、客訴樣本、極端 NG 樣本、模型上線前額外驗證。Evaluation Dataset 同樣隸屬於 Project。

Evaluation Result 需綁定：`project_id / model_version_id / dataset_version_id 或 evaluation_dataset_id / metrics_json / report_path / sample_predictions_path`

## 資料表與關聯

`users, projects, base_models, trainer_registry, dataset_versions, training_servers, training_workers, training_jobs, checkpoints, model_versions, evaluation_datasets, evaluation_results`

重要關聯：

- `projects` 1—N `dataset_versions` / `training_jobs` / `model_versions`
- `training_jobs` 1—1 `model_versions`，1—N `checkpoints`
- `model_versions` N—1 `base_models`，N—1 `projects`
- `model_versions` 可透過 `parent_model_version_id` 指向前一版模型
