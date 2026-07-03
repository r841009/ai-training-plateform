# 緊急修正：模型授權安全控管

日期：2026-07-03

## 背景

產線可能採代工 / OEM / 客戶專案模式，因此平台不能只列出模型名稱，必須記錄模型來源、授權模式、商用與 OEM 使用限制，並在建立 Training Job 時避免誤用高風險模型。

## 授權 Survey 摘要

- Ultralytics YOLO：官方授權頁指出商業產品、閉源、SaaS、嵌入式、customer-facing solution、fine-tuned YOLO model 等情境需要 Ultralytics Enterprise License，否則需遵守 AGPL-3.0 開源義務。
  - https://www.ultralytics.com/license
- torchvision：BSD-3-Clause。
  - https://github.com/pytorch/vision/blob/main/LICENSE
- Detectron2：Apache-2.0。
  - https://github.com/facebookresearch/detectron2/blob/main/LICENSE
- YOLOX：Apache-2.0。
  - https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE
- MMDetection：Apache-2.0。
  - https://github.com/open-mmlab/mmdetection/blob/main/LICENSE
- PaddleDetection：Apache-2.0。
  - https://github.com/PaddlePaddle/PaddleDetection/blob/develop/LICENSE
- DETR：Apache-2.0。
  - https://github.com/facebookresearch/detr/blob/main/LICENSE

## 已完成項目

- `base_models` 增加授權欄位：
  - `source_provider`
  - `license_name`
  - `license_url`
  - `license_risk_level`
  - `commercial_use_allowed`
  - `oem_use_allowed`
  - `requires_enterprise_license`
  - `license_notes`
- YOLOv8 / YOLOv11 標為 HIGH risk、需要 enterprise license、不可 OEM。
- Training Job 建立時，會阻擋未核准 OEM 或需要 enterprise license 的 base model。
- Training Job 建立時，會檢查 trainer `base_model_family` 是否支援 selected base model family。
- 新增較適合 OEM/商用評估的替代 detection base models：
  - `fasterrcnn_resnet50_fpn`
  - `retinanet_resnet50_fpn`
  - `ssd300_vgg16`
  - `fcos_resnet50_fpn`
  - `yolox_s`
  - `yolox_m`
  - `detectron2_fasterrcnn_r50_fpn`
  - `detectron2_retinanet_r50_fpn`
  - `detr_resnet50`
  - `rt_detr_r50`
  - `mmdet_retinanet_r50_fpn`
- 新增對應 trainer catalog entries，作為 Phase 9-10 實作接口預留。

## 注意

這是工程側風險控管，不等同法律意見。正式量產 / 客戶交付前，仍需法務或授權窗口確認實際使用的 code、weights、pretrained checkpoints、dataset 與部署方式。

