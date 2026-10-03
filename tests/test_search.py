def test_search_endpoint_success(client, mock_qdrant, mock_embedder):
    res = client.get("/api/search?q=computer")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert data["query"] == "computer"


def test_search_endpoint_empty_query(client):
    res = client.get("/api/search?q=")
    assert res.status_code == 422 or res.status_code == 400
