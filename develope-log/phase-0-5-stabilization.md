# Phase 0-5：測試穩定化修復

日期：2026-07-03

## 目標

在進入 Phase 6 前，先修復既有 Phase 0-5 測試於目前 Windows 開發環境中的不穩定問題。

## 已完成項目

- 修正 Windows 上 zip upload 會因 `NamedTemporaryFile` 檔案鎖定而回 422 的問題。
- 修正 health test 直接連真實 PostgreSQL，導致沒有 DB 時測試逾時的問題。
- 新增 health check 對 DB unavailable 情境的測試。

## 產生 / 修改的檔案

```
backend/app/services/dataset_version_service.py
backend/tests/test_health.py
develope-log/phase-0-5-stabilization.md
```

## 如何測試

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

實測結果：`38 passed`。

## 下一步

Phase 6：Training Server Resource Monitor。

