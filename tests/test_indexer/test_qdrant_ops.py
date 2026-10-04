from app.indexer.qdrant_ops import (
    build_point,
    ensure_collection,
    check_file_exists_and_unchanged,
    delete_points_by_file_path,
    delete_points_under_folder,
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


def test_folder_delete_uses_indexed_root_filter(mock_qdrant):
    result = delete_points_under_folder(
        mock_qdrant,
        "knowledge_base",
        r"C:\docs",
        timeout=30,
    )

    assert result["direct_delete_succeeded"] is True
    selector = mock_qdrant.delete.call_args.kwargs["points_selector"]
    condition = selector.filter.must[0]
    assert condition.key == "index_roots"
    assert condition.match.value == r"C:\docs"


def test_folder_delete_legacy_fallback_is_separator_aware():
    class Record:
        def __init__(self, point_id, file_path):
            self.id = point_id
            self.payload = {"file_path": file_path}

    class Client:
        def __init__(self):
            self.page = 0
            self.deleted = []

        def delete(self, **kwargs):
            selector = kwargs["points_selector"]
            if hasattr(selector, "points"):
                self.deleted.extend(selector.points)

        def scroll(self, **kwargs):
            self.page += 1
            if self.page == 1:
                return [
                    Record("inside", r"C:\docs\file.txt"),
                    Record("sibling", r"C:\docs2\file.txt"),
                ], "next"
            return [], None

    client = Client()
    result = delete_points_under_folder(
        client,
        "knowledge_base",
        r"C:\docs",
        legacy_fallback=True,
        page_size=2,
        delete_batch_size=1,
    )

    assert result["legacy_points_deleted"] == 1
    assert client.deleted == ["inside"]


def test_build_point_stores_normalized_index_roots():
    point = build_point(
        r"C:\Docs\file.txt",
        {"chunk_index": 0, "text": "content"},
        [0.0],
        index_roots=[r"C:\Docs", r"C:/Docs"],
    )

    assert point["payload"]["file_path"] == r"C:\Docs\file.txt"
    assert point["payload"]["index_roots"] == [r"C:\Docs"]


def test_folder_delete_retries_legacy_qdrant_arguments():
    class Client:
        def __init__(self):
            self.delete_calls = []
            self.scroll_calls = []

        def delete(self, **kwargs):
            self.delete_calls.append(kwargs)
            if "timeout" in kwargs or "wait" in kwargs:
                raise TypeError("legacy client does not accept this argument")

        def scroll(self, **kwargs):
            self.scroll_calls.append(kwargs)
            if "timeout" in kwargs or kwargs.get("with_payload") != True:
                raise TypeError("legacy client only supports full payload")
            return [], None

    client = Client()
    result = delete_points_under_folder(
        client,
        "knowledge_base",
        r"C:\docs",
        timeout=2.2,
    )

    assert result["direct_delete_succeeded"] is True
    assert len(client.delete_calls) == 3
    assert len(client.scroll_calls) == 3
    assert client.scroll_calls[-1]["with_payload"] is True
