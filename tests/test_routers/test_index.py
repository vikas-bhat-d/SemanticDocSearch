def test_index_status_endpoint(authenticated_client):
    res = authenticated_client.get("/api/index/status")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data


def test_index_start_unauthorized(client):
    res = client.post("/api/index/start")
    assert res.status_code == 401


def test_index_stop_when_not_running(authenticated_client):
    res = authenticated_client.post("/api/index/stop")
    assert res.status_code == 400
