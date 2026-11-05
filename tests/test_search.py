def test_search_endpoint_success(client, mock_qdrant, mock_embedder):
    res = client.get("/api/search?q=computer")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert data["query"] == "computer"


def test_search_endpoint_accepts_custom_weights(client, mock_qdrant, mock_embedder):
    res = client.get(
        "/api/search?q=computer&semantic_weight=0.7&keyword_weight=0.3"
    )

    assert res.status_code == 200
    query = mock_qdrant.query_points.call_args.kwargs
    assert query["query"].rrf.weights == [0.7, 0.3]


def test_search_endpoint_zero_weight_selects_keyword_only(
    client, mock_qdrant, mock_embedder
):
    res = client.get(
        "/api/search?q=computer&semantic_weight=0&keyword_weight=1"
    )

    assert res.status_code == 200
    mock_embedder.embed_batch.assert_not_called()
    query = mock_qdrant.query_points.call_args.kwargs
    assert query["using"] == "content"
    assert "prefetch" not in query


def test_search_endpoint_rejects_both_weights_zero(client, mock_qdrant):
    res = client.get(
        "/api/search?q=computer&semantic_weight=0&keyword_weight=0"
    )

    assert res.status_code == 422
    assert "At least one" in res.json()["detail"]
    mock_qdrant.query_points.assert_not_called()


def test_search_endpoint_empty_query(client):
    res = client.get("/api/search?q=")
    assert res.status_code == 422 or res.status_code == 400
