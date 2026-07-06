# Phase 1 Ponytail Review

日期：2026-07-06

backend/app/config.py:L9: delete: unused `app_env` setting. Nothing replaces it until code branches on environment.
backend/app/config.py:L18-L32: delete: unused Redis settings and `redis_url`. Nothing replaces them until a Redis-backed feature lands.
backend/app/logging_config.py:L1-L10 and backend/app/main.py:L5,L18: yagni: one-function logging module called once. Inline `logging.basicConfig(...)` in `main.py` and delete the module.
backend/tests/test_health.py:L1-L6: shrink: local module-level `TestClient`. Use the existing `client` fixture and delete the import/client setup.

net: -19 lines possible.
