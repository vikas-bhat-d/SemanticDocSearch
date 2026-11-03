from app.search.engine import SearchEngine
from qdrant_client import models


def test_search_engine_basic(db_session, mock_qdrant, mock_embedder):
    engine = SearchEngine(db_session)
    res = engine.search(
        query="computer hardware",
        departments=["HR"],
        doc_types=["CL"],
        extensions=[".docx"],
    )

    assert res["query"] == "computer hardware"
    assert "results" in res
    assert res["page"] == 1
    query = mock_qdrant.query_points.call_args.kwargs
    assert query["query"] == models.FusionQuery(fusion=models.Fusion.RRF)
    assert query["prefetch"][0].query == models.TextQuery(text="computer hardware")
    assert query["prefetch"][0].using == "content"
    assert query["prefetch"][1].query == [0.0] * 384
    for prefetch in query["prefetch"]:
        assert [condition.key for condition in prefetch.filter.must] == [
            "departments",
            "doc_types",
            "file_extension",
        ]


def test_search_engine_exact_mode_keeps_dense_search(db_session, mock_qdrant, mock_embedder):
    engine = SearchEngine(db_session)

    engine.search(query="computer hardware", exact=True)

    query = mock_qdrant.query_points.call_args.kwargs
    assert "prefetch" not in query
    assert query["query"] == [0.0] * 384
