import threading
import time
from types import SimpleNamespace

from app.indexer.converter import DocumentConverter, FileSizeLimitError
from app.indexer.runner import CounterBatch, IndexerRunner
from sqlalchemy.orm import sessionmaker

from app.indexer.paths import canonical_file_path
from app.indexer.qdrant_ops import (
    deterministic_point_id,
    iter_bounded_point_batches,
    update_payload_for_file,
)
from app.indexer.traverser import walk_folders_stream
from app.models import IndexFolder, IndexRun


def test_producer_wait_allows_slow_discovery_to_finish():
    runner = IndexerRunner()
    producer = threading.Thread(target=lambda: time.sleep(0.05))
    producer.start()

    assert runner._wait_for_producer(producer, shutdown_timeout=0.001) is True


def test_runner_skips_empty_file_without_failing(monkeypatch, db_session, tmp_path):
    import app.indexer.runner as runner_module

    file_path = tmp_path / "empty.md"
    file_path.write_bytes(b"")
    run = IndexRun(status="running")
    db_session.add(run)
    db_session.commit()

    config = SimpleNamespace(
        collection_name="knowledge_base",
        qdrant_timeout_seconds=1,
        chunk_size=512,
        chunk_overlap=64,
    )
    monkeypatch.setattr(runner_module, "is_already_indexed", lambda *args, **kwargs: False)
    monkeypatch.setattr(runner_module, "delete_points_by_file_path", lambda *args, **kwargs: None)

    runner = IndexerRunner()
    runner._record_detail = lambda *args, **kwargs: None
    counts = CounterBatch()
    runner._process_item(
        run.id,
        {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "extension": ".md",
            "force_reindex": False,
        },
        db_session,
        config,
        DocumentConverter(),
        None,
        object(),
        counts,
        SimpleNamespace(info=lambda *args, **kwargs: None),
    )

    assert counts.values == {"skipped": 1, "processed": 1}
    assert not runner._failure_event.is_set()


def test_runner_skips_file_size_limit_without_failing(monkeypatch, db_session, tmp_path):
    import app.indexer.runner as runner_module

    file_path = tmp_path / "large.md"
    file_path.write_text("content", encoding="utf-8")
    run = IndexRun(status="running")
    db_session.add(run)
    db_session.commit()

    config = SimpleNamespace(
        collection_name="knowledge_base",
        qdrant_timeout_seconds=1,
        chunk_size=512,
        chunk_overlap=64,
    )
    monkeypatch.setattr(runner_module, "is_already_indexed", lambda *args, **kwargs: False)
    monkeypatch.setattr(runner_module, "delete_points_by_file_path", lambda *args, **kwargs: None)

    class SizeLimitedConverter:
        def convert(self, path):
            raise FileSizeLimitError("exceeds maximum limit")

    runner = IndexerRunner()
    runner._record_detail = lambda *args, **kwargs: None
    counts = CounterBatch()
    runner._process_item(
        run.id,
        {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "extension": ".md",
            "force_reindex": False,
        },
        db_session,
        config,
        SizeLimitedConverter(),
        None,
        object(),
        counts,
        SimpleNamespace(info=lambda *args, **kwargs: None),
    )

    assert counts.values == {"skipped": 1, "processed": 1}
    assert not runner._failure_event.is_set()


def test_point_batches_are_bounded_and_ids_are_deterministic():
    points = [
        {"payload": {"file_path": r"C:\Docs\a.txt", "chunk_index": i}, "vector": [0.0]}
        for i in range(5)
    ]
    batches = list(iter_bounded_point_batches(points, max_points=2, max_bytes=4096))

    assert [len(batch) for batch in batches] == [2, 2, 1]
    assert batches[0][0]["id"] == deterministic_point_id(r"C:\Docs\a.txt", 0)


def test_traverser_is_lazy_and_honors_changed_deleted_paths(db_session, tmp_path):
    indexed_root = tmp_path / "docs"
    indexed_root.mkdir()
    changed = indexed_root / "changed.txt"
    deleted = indexed_root / "deleted.txt"
    ordinary = indexed_root / "ordinary.txt"
    for path in (changed, deleted, ordinary):
        path.write_text(path.name, encoding="utf-8")

    db_session.add(IndexFolder(path=str(indexed_root)))
    db_session.commit()
    changed_key = canonical_file_path(str(changed))
    deleted_key = canonical_file_path(str(deleted))

    items = list(walk_folders_stream(
        db_session,
        threading.Event(),
        {changed_key},
        {deleted_key},
    ))
    pending = {item["canonical_path"]: item for item in items if item["status"] == "pending"}

    assert deleted_key not in pending
    assert pending[changed_key]["force_reindex"] is True
    assert pending[canonical_file_path(str(ordinary))]["force_reindex"] is False


def test_reclassify_scrolls_all_pages():
    class Client:
        def __init__(self):
            self.page = 0
            self.updated = []

        def scroll(self, **kwargs):
            self.page += 1
            if self.page == 1:
                return [type("Point", (), {"id": 1})(), type("Point", (), {"id": 2})()], "next"
            return [type("Point", (), {"id": 3})()], None

        def set_payload(self, **kwargs):
            self.updated.append(kwargs["points"])

    client = Client()
    assert update_payload_for_file(client, "knowledge_base", r"C:\a.txt", ["D"], ["T"]) == 3
    assert client.updated == [[1, 2], [3]]


def test_runner_processes_bounded_batches(monkeypatch, db_session, tmp_path):
    import app.indexer.runner as runner_module

    root = tmp_path / "docs"
    root.mkdir()
    (root / "a.txt").write_text("one two three four five six seven eight", encoding="utf-8")
    db_session.add(IndexFolder(path=str(root)))
    db_session.commit()
    factory = sessionmaker(bind=db_session.bind, autoflush=False, autocommit=False)
    monkeypatch.setattr(runner_module, "SessionLocal", factory)

    config = SimpleNamespace(
        index_workers=1,
        index_queue_capacity=1,
        embedding_batch_size=2,
        embedding_concurrency=1,
        qdrant_upsert_batch_size=1,
        qdrant_upsert_max_bytes=4096,
        qdrant_timeout_seconds=1,
        queue_put_timeout_seconds=0.01,
        worker_shutdown_timeout_seconds=2,
        counter_flush_interval=1,
        collection_name="knowledge_base",
        qdrant_host="localhost",
        qdrant_port=6333,
        embedding_model="test",
        embedding_dimensions=2,
        max_file_size_mb=100,
        max_markdown_chars=10000,
        max_chunk_chars=1000,
        conversion_timeout_seconds=2,
        chunk_size=2,
        chunk_overlap=0,
        rows_per_chunk=2,
    )
    monkeypatch.setattr(runner_module, "get_config", lambda db: config)
    monkeypatch.setattr(runner_module, "DocumentConverter", lambda **kwargs: type(
        "Converter", (), {"convert": lambda self, path: open(path, encoding="utf-8").read()}
    )())

    class Qdrant:
        def __init__(self):
            self.upsert_sizes = []

        def scroll(self, **kwargs):
            return [], None

        def upsert(self, **kwargs):
            self.upsert_sizes.append(len(kwargs["points"]))

        def delete(self, **kwargs):
            return None

        def close(self):
            pass

    qdrant = Qdrant()
    monkeypatch.setattr(runner_module, "get_qdrant_client", lambda **kwargs: qdrant)
    monkeypatch.setattr(runner_module, "ensure_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr(runner_module, "Embedder", lambda **kwargs: type(
        "Embedder", (), {"embed_batch": lambda self, texts: [[0.0, 0.0] for _ in texts]}
    )())

    run = IndexRun(status="running")
    db_session.add(run)
    db_session.commit()
    runner = runner_module.IndexerRunner()
    runner.is_running = True
    runner.current_run_id = run.id
    runner._execute_run(run.id, None, None)

    db_session.expire_all()
    refreshed = db_session.get(IndexRun, run.id)
    assert refreshed.status == "completed"
    assert refreshed.discovered_files == 1
    assert refreshed.processed_files == 1
    assert max(qdrant.upsert_sizes) <= 1


def test_runner_marks_run_failed_when_file_processing_fails(monkeypatch, db_session, tmp_path):
    import app.indexer.runner as runner_module

    root = tmp_path / "docs"
    root.mkdir()
    (root / "a.txt").write_text("content", encoding="utf-8")
    db_session.add(IndexFolder(path=str(root)))
    db_session.commit()
    factory = sessionmaker(bind=db_session.bind, autoflush=False, autocommit=False)
    monkeypatch.setattr(runner_module, "SessionLocal", factory)

    config = SimpleNamespace(
        index_workers=1,
        index_queue_capacity=1,
        embedding_batch_size=2,
        embedding_concurrency=1,
        qdrant_upsert_batch_size=1,
        qdrant_upsert_max_bytes=4096,
        qdrant_timeout_seconds=1,
        queue_put_timeout_seconds=0.01,
        worker_shutdown_timeout_seconds=2,
        counter_flush_interval=1,
        collection_name="knowledge_base",
        qdrant_host="localhost",
        qdrant_port=6333,
        embedding_model="test",
        embedding_dimensions=2,
        max_file_size_mb=100,
        max_markdown_chars=10000,
        max_chunk_chars=1000,
        conversion_timeout_seconds=2,
        chunk_size=2,
        chunk_overlap=0,
        rows_per_chunk=2,
    )
    monkeypatch.setattr(runner_module, "get_config", lambda db: config)
    monkeypatch.setattr(runner_module, "DocumentConverter", lambda **kwargs: type(
        "Converter", (), {
            "convert": lambda self, path: (_ for _ in ()).throw(
                ValueError("conversion failed")
            )
        }
    )())

    class Qdrant:
        def get_collections(self):
            return type("Collections", (), {"collections": []})()

        def scroll(self, **kwargs):
            return [], None

        def delete(self, **kwargs):
            return None

        def close(self):
            pass

    monkeypatch.setattr(runner_module, "get_qdrant_client", lambda **kwargs: Qdrant())
    monkeypatch.setattr(runner_module, "ensure_collection", lambda *args, **kwargs: None)
    monkeypatch.setattr(runner_module, "Embedder", lambda **kwargs: object())

    run = IndexRun(status="running")
    db_session.add(run)
    db_session.commit()
    runner = runner_module.IndexerRunner()
    runner.is_running = True
    runner.current_run_id = run.id
    runner._execute_run(run.id, None, None)

    db_session.expire_all()
    refreshed = db_session.get(IndexRun, run.id)
    assert refreshed.status == "failed"
    assert refreshed.failed_files == 1
    assert refreshed.processed_files == 1
