# Phase 8 Ponytail Review

日期：2026-07-06

backend/app/services/scheduler_service.py:L14-L19: yagni: `ResourceRequirement` dataclass only exists as a one-hop parse container. Inline parsed values in `_server_can_run` or return a plain dict.
backend/app/services/scheduler_service.py:L31-L33: shrink: manual `dispatched` / `queued` / `failed` counters. Build decisions, then sum by status from decisions.
backend/app/services/scheduler_service.py:L85-L92: shrink: manual first-match loop. `next((s for s in servers if self._server_can_run(s, requirement)), None)`.
backend/app/services/scheduler_service.py:L94-L96: yagni: one-line `_dataset_ready` wrapper used once. Inline `dataset is not None and dataset.status == "READY"`.
backend/app/schemas/scheduler.py:L6-L18: Lean already. Ship.
backend/app/routers/scheduler.py:L9-L19: Lean already. Ship.

net: -15 lines possible.

## 修正紀錄

日期：2026-07-06

- 已移除 `ResourceRequirement` dataclass，直接用 `resource_requirement_json` dict 做資源判斷。
- 已移除 one-line `_dataset_ready()` helper，改在 `dispatch_once()` 內直接判斷 dataset 是否 READY。
- 已將 `_find_server_for_job()` 的 manual first-match loop 改成 `next(...)`。
- 已移除 `dispatched` / `queued` / `failed` mutable counters，改由 `decisions` 聚合統計。

驗證：

- `tests/test_scheduler.py`：`4 passed`
- `tests/test_worker_manager.py`：`2 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
