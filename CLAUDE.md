你是一位資深軟體架構師與全端工程師，請協助我從零開始，循序漸進開發一套「AOI AI 訓練平台」。

請務必遵守以下原則：

1. 不要一次完成全部功能。
2. 每次只完成一個明確階段。
3. 每個階段開始前，先說明本階段目標、檔案變更範圍、預期產出。
4. 每個階段完成後，請列出：
   - 已完成項目
   - 產生或修改的檔案
   - 如何測試
   - 下一步建議
   完成後停下來回報，等待確認再進行下一階段。
5. 架構要保持可擴展、可維護、可測試。
6. 不要把訓練邏輯直接寫死在 Web API 裡。
7. 所有模型、資料集、訓練任務都必須以 Project 為範圍隔離。
8. 不同 Project 的 Model Versions 不可以混在同一個一般使用者頁面顯示。

# 一、專案目標

我要建立一套 AOI AI 訓練平台，讓使用者可以：

- 建立 AOI Project
- 在不同 Project 中獨立管理 Dataset Versions
- 選擇平台提供的 Base Model
- 上傳大量影像資料與標註資料
- 建立 Training Job
- 系統自動檢查 Training Server 資源
- 若資源足夠則派工訓練
- 若資源不足則進入 Queue
- 訓練過程支援 checkpoint
- 訓練中斷後可以 resume
- 每次訓練成功後產生 Project-scoped Model Version
- 可以對模型進行 validation、test、evaluation
- 可以基於既有 Model Version 進行 retrain
- Retrain 不覆蓋舊模型，而是產生新的 Model Version
- 可透過docker or k8s 進行快速展延或部署

# 二、核心架構

系統拆成 6 個模組，細節見 [ARCHITECTURE.md](ARCHITECTURE.md)：

1. Web / Backend API — 只做 CRUD 與狀態查詢，不可直接執行訓練
2. Scheduler / Dispatcher — 派工、resource-aware scheduling、trainer registry
3. Resource Monitor — 收集 Training Server 資源指標
4. Training Worker Manager — 啟動訓練程式、監控 process、回報 heartbeat
5. Training Script — 讀 config、寫 checkpoint / metrics、支援 resume
6. Storage Service — 上傳與 raw/processed dataset、checkpoint、model files 儲存

# 三、技術選型

第一版請優先採用：

- Frontend：Vue 3 + Element Plus
- Backend API：FastAPI
- Database：PostgreSQL
- Queue：Redis 或 RabbitMQ，先用較簡單可落地的方案
- Training Worker：Python
- AI Framework：PyTorch
- Detection Model：YOLO 系列先預留介面
- Storage：Local File System / NAS path，架構上保留未來 MinIO / S3 擴充
- Deployment：Docker Compose 優先，不要一開始上 Kubernetes

如果目前 repo 還沒有建立，請先產生清楚的 monorepo 結構。

# 四、Project-scoped Model 管理規則

平台層級只管理 Base Model，例如：

- YOLOv8n
- YOLOv8s
- YOLOv11n
- ResNet50
- EfficientNet
- U-Net

Project 層級管理訓練後產生的 Model Versions。

Model Version 一定要隸屬於 Project。

不同 Project 即使使用同一個 Base Model，也要獨立管理、獨立顯示、獨立 retrain。

一般使用者不應該看到全平台混合的 Model Versions 頁面。

正確 API 設計方向：

- GET /projects/{project_id}/model-versions
- POST /projects/{project_id}/training-jobs
- POST /projects/{project_id}/model-versions/{model_version_id}/retrain
- GET /projects/{project_id}/training-jobs
- GET /projects/{project_id}/datasets
- GET /projects/{project_id}/evaluation-results

避免一般功能使用：

- GET /model-versions

除非是 Admin 後台總覽。

# 五、Model Version 命名規則

Model Version 的人類可讀名稱使用：

{project_code}{base_model}{YYYYMMDD_HHmmss}

範例：

LED_SCRATCH_yolov8s_20260702_153000
PCB_STAIN_yolov8s_20260702_160000

但系統內部不要只靠名稱判斷版本關係。

必須用資料庫欄位管理：

- project_id
- base_model_id
- training_job_id
- dataset_version_id
- parent_model_version_id
- version_no
- created_at

Retrain 時：

- 不覆蓋舊模型
- 基於 parent_model_version_id
- 使用新的 dataset_version_id 或新的 training config
- 產生新的 model_version

# 六、Dataset 與資料模型

Dataset Version 狀態、儲存結構、manifest 格式、train/val/test split、Evaluation Dataset、資料表關聯，見 [DATASET.md](DATASET.md)。

# 七、程式碼品質要求

請遵守：

- 清楚分層，不要把 business logic 塞在 router，使用 service layer + repository / data access layer
- 使用 Pydantic schema、使用 migration
- 所有 API 要有基本錯誤處理
- 所有 Project-scoped API 都要驗證 project_id
- 所有 retrain 都要檢查 parent_model_version 是否屬於同一個 Project
- 所有資料路徑都要避免硬編碼，改用 config；訓練目錄與模型目錄要可配置
- README 要持續更新

# 八、開發階段

請依照 [PROGRESS.md](PROGRESS.md) 的 Phase 0 ~ Phase 16 循序完成。現在請先從 Phase 0 開始。

