# 文件整併記錄

日期：2026-07-02

## 背景

初始規劃文件（CLAUDE.md 之外另有 8 份）內容零散：6 個 Architecture_*.md 每份僅 5~20 行，且 CLAUDE.md / Dataset_design.md / Train_Validation_Test.md / Architecture_scheduler.md / Architecture_training_script.md / PROGRESS.md 之間存在斷裂的中文數字章節編號（六~十六），像是同一份文件被硬切開但未重新整理。

## 調整內容

9 個文件 → 4 個，每項調整前都先核對是否為純重複（無資訊損失才刪，否則只合併/改排版）：

- `Architecture_web.md` / `Architecture_scheduler.md` / `Architecture_monitor.md` / `Architecture_workmanager.md` / `Architecture_training_script.md` / `Architecture_storage.md` → 合併為 `ARCHITECTURE.md`（6 個模組改為 `##`/`###` 子標題，內容逐條核對無遺漏）
- `Dataset_design.md` + `Train_Validation_Test.md` → 合併為 `DATASET.md`
- `PROGRESS.md` 刪除「十五、程式碼品質要求」→ 搬到 CLAUDE.md（屬永久規則，非循序 Phase 內容）
- `PROGRESS.md` 刪除「十六、現在請先從 Phase 0 開始」→ 與檔案開頭 Phase 0 目標完全重複，無新資訊
- `PROGRESS.md` 每個 Phase 結尾「完成後先停下來回報。」共 16 處重複 → 刪除，改為 CLAUDE.md 全域規則 + PROGRESS.md 開頭一句話講一次

## 結果

| 檔案 | 行數 | 內容 |
|---|---|---|
| CLAUDE.md | 149 | 專案規則、目標、技術選型、命名規則、程式碼品質要求、階段指引 |
| ARCHITECTURE.md | 118 | 6 個模組架構 |
| DATASET.md | 69 | Dataset 設計、資料表關聯 |
| PROGRESS.md | 203 | Phase 0~16 清單（略超 200 行，因每個 Phase 的驗收項目是後續實作依據，判斷有影響故不精簡） |

未動：CLAUDE.md 原有「一、專案目標」~「五、Model Version 命名規則」，內容本來就精簡，無冗餘可刪。
