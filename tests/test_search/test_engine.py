from app.search.engine import SearchEngine


def test_search_engine_basic(db_session, mock_qdrant, mock_embedder):
    engine = SearchEngine(db_session)
    res = engine.search(query="computer hardware")

    assert res["query"] == "computer hardware"
    assert "results" in res
    assert res["page"] == 1
