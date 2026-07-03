from fastapi.testclient import TestClient

from app.routers import health as health_router
from app.main import app

client = TestClient(app)


def test_health_returns_ok_envelope(monkeypatch):
    monkeypatch.setattr(health_router, "ping_db", lambda: True)

    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["database"] == "ok"


def test_health_reports_unavailable_when_db_ping_fails(monkeypatch):
    def fail_ping():
        raise RuntimeError("db down")

    monkeypatch.setattr(health_router, "ping_db", fail_ping)

    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["database"] == "unavailable"


def test_404_uses_common_error_envelope():
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "404"
