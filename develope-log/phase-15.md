# Phase 15：Frontend

日期：2026-07-06

## 目標

建立 Vue 3 + Element Plus 前端，支援 Project List / Project Detail，並在 Project Detail 內提供 Dataset、Training Job、Model Version、Evaluation、Retrain 操作。

## 已完成項目

- 新增 `frontend/index.html`
  - 使用 Vue 3 + Element Plus CDN
  - 不需要 Node / npm 即可用 Python static server 啟動
- 新增 `frontend/src/app.js`
  - 內建 standalone mock API，沒有 PostgreSQL / Redis / backend 時也能先測 UI
  - Project List / Project create
  - Project Detail Overview
  - Dataset Version create / upload / process
  - Training Job create / resume
  - Scheduler dispatch-once
  - Model Version list
  - Model Version evaluate / retrain
  - Evaluation Dataset create
  - Evaluation Result list
- 新增 `frontend/src/styles.css`
  - 操作台式 layout
  - Project sidebar + detail tabs
- Backend `main.py` 加入 localhost CORS，支援前端呼叫 API。

## 如何測試

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
python -m http.server 5173 --directory frontend
```

開啟：

```text
http://127.0.0.1:5173?mock=1
```

實測結果：

- Backend tests：`69 passed`

## 已知限制

- 目前採 CDN 版 Vue / Element Plus，尚未建立 Vite build pipeline。
- 預設使用 standalone mock API；接真實 backend 時需設定 `localStorage.apiBase`。
- 前端尚未加入自動化 UI 測試。
- Training Server 註冊 / heartbeat 仍需透過 API 或測試工具建立，前端只提供 dispatch。

## 下一步

Phase 16：整合測試。使用前端與 API 串起 Project、Dataset、Training Job、Worker、Model Version、Evaluation、Retrain 流程。
