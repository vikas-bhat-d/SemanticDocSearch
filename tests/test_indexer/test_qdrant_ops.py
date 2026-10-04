from app.indexer.qdrant_ops import (
    ensure_collection,
    check_file_exists_and_unchanged,
    delete_points_by_file_path,
    is_already_indexed,
    upsert_point_batch,
    upsert_file_chunks
)


def test_qdrant_ops_wrapper(mock_qdrant):
    ensure_collection(mock_qdrant, "knowledge_base", 384)
    assert mock_qdrant.get_collections.called

    exists = check_file_exists_and_unchanged(mock_qdrant, "knowledge_base", r"C:\test.docx", "2024-01-01T00:00:00")
    assert exists is False

    res = delete_points_by_file_path(mock_qdrant, "knowledge_base", r"C:\test.docx")
    assert res == 1

    upsert_file_chunks(mock_qdrant, "knowledge_base", [{
        "vector": [0.0] * 384,
        "payload": {"file_path": r"C:\test.docx"}
    }])
    assert mock_qdrant.upsert.called


def test_qdrant_timeouts_are_integer_seconds(mock_qdrant):
    is_already_indexed(mock_qdrant, "knowledge_base", r"C:\test.docx", timeout=30.0)
    assert mock_qdrant.scroll.call_args.kwargs["timeout"] == 30

    delete_points_by_file_path(
        mock_qdrant, "knowledge_base", r"C:\test.docx", timeout=30.0
    )
    assert mock_qdrant.delete.call_args.kwargs["timeout"] == 30

    upsert_point_batch(
        mock_qdrant,
        "knowledge_base",
        [{"id": "test-point", "vector": [0.0], "payload": {"file_path": r"C:\test.docx"}}],
        timeout=30.0,
    )
    assert mock_qdrant.upsert.call_args.kwargs["timeout"] == 30
