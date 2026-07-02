from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok_envelope():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


def test_404_uses_common_error_envelope():
    resp = client.get("/does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "404"
