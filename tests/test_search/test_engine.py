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
    assert query["query"] == models.RrfQuery(
        rrf=models.Rrf(weights=[1.0, 1.0])
    )
    assert query["prefetch"][0].query == [0.0] * 384
    assert query["prefetch"][1].query == models.TextQuery(text="computer hardware")
    assert query["prefetch"][1].using == "content"
    for prefetch in query["prefetch"]:
        assert [condition.key for condition in prefetch.filter.must] == [
            "departments",
            "doc_types",
            "file_extension",
        ]


def test_search_engine_exact_mode_keeps_dense_search(db_session, mock_qdrant, mock_embedder):
    engine = SearchEngine(db_session)

    engine.search(
        query="computer hardware",
        exact=True,
        semantic_weight=1.0,
        keyword_weight=0.0,
    )

    query = mock_qdrant.query_points.call_args.kwargs
    assert "prefetch" not in query
    assert query["query"] == [0.0] * 384


def test_search_engine_keyword_only_skips_embedding(db_session, mock_qdrant, mock_embedder):
    engine = SearchEngine(db_session)

    engine.search(
        query="computer hardware",
        semantic_weight=0.0,
        keyword_weight=1.0,
    )

    mock_embedder.embed_batch.assert_not_called()
    query = mock_qdrant.query_points.call_args.kwargs
    assert query["query"] == models.TextQuery(text="computer hardware")
    assert query["using"] == "content"
    assert "prefetch" not in query


def test_search_engine_semantic_only_skips_keyword_retrieval(
    db_session, mock_qdrant, mock_embedder
):
    engine = SearchEngine(db_session)

    engine.search(
        query="computer hardware",
        semantic_weight=1.0,
        keyword_weight=0.0,
    )

    query = mock_qdrant.query_points.call_args.kwargs
    assert query["query"] == [0.0] * 384
    assert "prefetch" not in query
    assert "using" not in query
