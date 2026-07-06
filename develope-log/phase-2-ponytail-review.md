# Phase 2 Ponytail Review

日期：2026-07-06

backend/app/schemas/project.py:L1-L20: native: manual regex constant and field validator for `project_code`. Use `Field(pattern=r"^[A-Z0-9_]+$")` and delete `re`, `PROJECT_CODE_PATTERN`, and `validate_project_code()`.
backend/app/services/project_service.py:L20-L23: shrink: single-use `project` variable. `return self.repo.create(Project(...))`.
backend/app/routers/projects.py:L20-L21: shrink: single-use `project` variable. Inline `service.create_project(...)` in `ProjectRead.model_validate(...)`.
backend/app/routers/projects.py:L26-L27: shrink: single-use `projects` variable. Inline `service.list_projects()` in the response comprehension.
backend/app/routers/projects.py:L32-L33: shrink: single-use `project` variable. Inline `service.get_project(...)` in `ProjectRead.model_validate(...)`.
backend/app/routers/projects.py:L40-L41: shrink: single-use `project` variable. Inline `service.update_project(...)` in `ProjectRead.model_validate(...)`.

net: -18 lines possible.

## 修正紀錄

日期：2026-07-06

- 已改用 Pydantic `Field(pattern=r"^[A-Z0-9_]+$")` 驗證 `project_code`，移除 `re`、`PROJECT_CODE_PATTERN` 與 `field_validator`。
- 已移除 `ProjectService.create_project()` 中單次使用的 `project` 變數，直接 `return self.repo.create(Project(...))`。
- 已 inline `projects` router 中 create/list/get/update 的單次使用變數。

驗證：

- `tests/test_projects.py`：`5 passed`
- 全量 backend tests：`60 passed`
- Alembic head：`c1d2e3f4a5b6`
