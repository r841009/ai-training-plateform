# Phase 9 Ponytail Review

日期：2026-07-06

worker/worker_manager.py:L3-L13: native: manual sys.path injection to import backend app. Package/PYTHONPATH/pytest pythonpath config replaces it.
backend/tests/test_worker_manager.py:L2-L11: native: second manual sys.path injection for test imports. Same package/PYTHONPATH setup replaces it.
worker/worker_manager.py:L32-L34: yagni: TrainerRunner Protocol with one implementation. Pass a callable or concrete runner until Phase 10 introduces a second real runner.
worker/worker_manager.py:L90-L103: delete: skipped result uses fake UUID(int=0) for missing server. Return empty results with skipped=1, or raise ValueError.
worker/worker_manager.py:L107-L125: shrink: manual succeeded/failed counters. Build results then use sum(r.status == "SUCCESS" for r in results) and sum(r.status == "FAILED" for r in results).
worker/worker_manager.py:L136: shrink: custom exception log prefix plus traceback string. traceback.format_exc() alone is enough for worker.log.
README.md:L65-L76: shrink: Worker Manager details duplicate worker/README.md. Keep command in README, move detailed log path notes to worker/README.md.

net: -25 lines possible.

## 修正紀錄

日期：2026-07-06

- 已移除 `worker/worker_manager.py` 的 manual `sys.path` injection，改由 `PYTHONPATH` / pytest 設定處理 import path。
- 已移除 `backend/tests/test_worker_manager.py` 的 manual `sys.path` injection。
- 已新增 `backend/pytest.ini`，讓 pytest 可同時 import `backend/app` 與 repo root 下的 `worker` package。
- 已移除只有單一實作的 `TrainerRunner Protocol`。
- 已移除 missing server 分支中的 fake `uuid.UUID(int=0)` result，改回傳空 results + `skipped=1`。
- 已將 worker success / failed counters 改成由 results 聚合。
- 已簡化 trainer exception log，只寫入 `traceback.format_exc()`。
- 已縮短 README Worker Manager 區塊，詳細說明保留在 `worker/README.md`。

驗證：

- `tests/test_worker_manager.py`：`2 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
