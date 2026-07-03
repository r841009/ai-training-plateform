import uuid


def _create_training_server(client, hostname: str = "trainer-01") -> dict:
    resp = client.post(
        "/training-servers",
        json={"hostname": hostname, "ip_address": "10.0.0.11", "max_concurrent_jobs": 2},
    )
    assert resp.status_code == 201
    return resp.json()["data"]


def test_create_and_list_training_servers(client):
    server = _create_training_server(client)
    assert server["hostname"] == "trainer-01"
    assert server["status"] == "REGISTERED"
    assert server["gpu_count"] == 0
    assert server["max_concurrent_jobs"] == 2
    assert server["last_heartbeat_at"] is None

    resp = client.get("/training-servers")
    assert resp.status_code == 200
    assert [s["hostname"] for s in resp.json()["data"]] == ["trainer-01"]


def test_duplicate_training_server_hostname_rejected(client):
    _create_training_server(client, "trainer-dup")
    resp = client.post("/training-servers", json={"hostname": "trainer-dup"})
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_get_training_server(client):
    server = _create_training_server(client, "trainer-get")

    resp = client.get(f"/training-servers/{server['id']}")
    assert resp.status_code == 200
    assert resp.json()["data"]["hostname"] == "trainer-get"


def test_training_server_heartbeat_updates_resource_metrics(client):
    server = _create_training_server(client, "trainer-heartbeat")

    resp = client.post(
        f"/training-servers/{server['id']}/heartbeat",
        json={
            "status": "ONLINE",
            "gpu_count": 2,
            "gpu_memory_total_gb": 48.0,
            "gpu_memory_free_gb": 32.5,
            "gpu_utilization_percent": 41.2,
            "cpu_usage_percent": 55.0,
            "ram_total_gb": 128.0,
            "ram_free_gb": 96.0,
            "disk_free_gb": 512.0,
            "running_job_count": 1,
            "max_concurrent_jobs": 3,
        },
    )

    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["status"] == "ONLINE"
    assert body["gpu_count"] == 2
    assert body["gpu_memory_free_gb"] == 32.5
    assert body["cpu_usage_percent"] == 55.0
    assert body["running_job_count"] == 1
    assert body["max_concurrent_jobs"] == 3
    assert body["last_heartbeat_at"] is not None


def test_training_server_heartbeat_rejects_invalid_status(client):
    server = _create_training_server(client, "trainer-bad-status")

    resp = client.post(f"/training-servers/{server['id']}/heartbeat", json={"status": "BUSY"})
    assert resp.status_code == 422


def test_missing_training_server_returns_404(client):
    resp = client.get(f"/training-servers/{uuid.uuid4()}")
    assert resp.status_code == 404

    resp = client.post(f"/training-servers/{uuid.uuid4()}/heartbeat", json={})
    assert resp.status_code == 404

