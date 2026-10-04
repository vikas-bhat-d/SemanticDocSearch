import os
import queue
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from itertools import chain
from typing import Any, Dict, Optional, Set

from sqlalchemy.orm import Session

from app.config import get_config
from app.database import SessionLocal, db_write_lock
from app.indexer.chunker.registry import get_chunker
from app.indexer.classifier import classify_file
from app.indexer.converter import (
    DocumentConverter,
    EmptyContentError,
    FileSizeLimitError,
    UnsupportedFileTypeError,
)
from app.indexer.embedder import Embedder
from app.indexer.paths import canonical_file_path, normalize_file_path
from app.indexer.qdrant_ops import (
    delete_points_by_file_path,
    ensure_collection,
    get_qdrant_client,
    is_already_indexed,
    iter_point_batches,
    upsert_point_batch,
)
from app.indexer.traverser import (
    get_index_roots,
    iter_incremental_file_items,
    walk_folders_stream,
)
from app.indexer.xml_parser import parse_incremental_inputs
from app.logger import get_logger
from app.models import IndexFolder, IncrementalXmlConfig, IndexRun, IndexRunFile


def _pending_files_from_previous_stopped_run(db: Session, run_id: int):
    """Legacy helper retained for API/tests; new runs resume by rediscovery."""
    previous_run = (
        db.query(IndexRun)
        .filter(IndexRun.id < run_id)
        .order_by(IndexRun.id.desc())
        .first()
    )
    if not previous_run or previous_run.status != "stopped":
        return []
    return [
        run_file.file_path
        for run_file in db.query(IndexRunFile).filter_by(
            run_id=previous_run.id, status="pending"
        ).all()
    ]


class RunStopped(Exception):
    """Internal control flow for a cooperative stop, not a file failure."""


@dataclass
class CounterBatch:
    values: Dict[str, int] = field(default_factory=dict)
    terminal_count: int = 0
    last_flush: float = field(default_factory=time.monotonic)

    def add(self, **deltas: int):
        for key, value in deltas.items():
            self.values[key] = self.values.get(key, 0) + value
        self.terminal_count += deltas.get("processed", 0)

    def clear(self):
        self.values.clear()
        self.terminal_count = 0
        self.last_flush = time.monotonic()


class IndexerRunner:
    DETAIL_ROW_LIMIT = 250
    SCAN_FOLDER_STATUSES = ("pending", "failed", "stopped")

    def __init__(self):
        self.stop_event = threading.Event()
        self.is_running = False
        self.is_stopping = False
        self.current_run_id: Optional[int] = None
        self._thread: Optional[threading.Thread] = None
        self._state_lock = threading.RLock()
        self._failure_event = threading.Event()
        self._detail_lock = threading.Lock()
        self._detail_counts: Dict[int, int] = {}
        self._detail_capped: Set[int] = set()
        self._lease_owner: Optional[str] = None
        self._lease_stop = threading.Event()
        self._lease_thread: Optional[threading.Thread] = None
        self._lease_duration_seconds = 120.0

    def _empty_status(self) -> Dict[str, Any]:
        return {
            "status": "IDLE",
            "run_id": None,
            "total_files": 0,
            "discovered_files": 0,
            "discovery_complete": False,
            "processed_files": 0,
            "indexed_files": 0,
            "skipped_files": 0,
            "failed_files": 0,
            "deleted_files": 0,
            "progress_percentage": 0.0,
        }

    def _reconcile_abandoned_runs(self, db: Session, now: Optional[datetime] = None):
        """Mark runs whose lease expired while the process was unavailable."""
        now = now or datetime.utcnow()
        with db_write_lock:
            expired_runs = db.query(IndexRun.id).filter(
                IndexRun.status == "running",
                IndexRun.lease_expires_at.isnot(None),
                IndexRun.lease_expires_at < now,
            ).all()
            if not expired_runs:
                return
            db.query(IndexRun).filter(
                IndexRun.id.in_([run_id for (run_id,) in expired_runs]),
            ).update(
                {
                    "status": "failed",
                    "stopped_at": now,
                    "lease_owner": None,
                    "lease_expires_at": None,
                },
                synchronize_session=False,
            )
            db.query(IndexFolder).filter(
                IndexFolder.status == "indexing",
            ).update(
                {
                    "status": "failed",
                    "updated_at": now,
                },
                synchronize_session=False,
            )
            db.commit()

    def _reconcile_legacy_folder_statuses(
        self,
        db: Session,
        now: Optional[datetime] = None,
    ):
        """Backfill completion for folders scanned before folder statuses were maintained."""
        successful_full_runs = (
            db.query(IndexRun)
            .filter(
                IndexRun.status == "completed",
                IndexRun.stopped_at.isnot(None),
            )
            .order_by(IndexRun.id.desc())
            .all()
        )
        latest_full_run = next(
            (
                run
                for run in successful_full_runs
                if not run.changed_xml_path and not run.deleted_xml_path
            ),
            None,
        )
        if not latest_full_run or not latest_full_run.stopped_at:
            return

        db.query(IndexFolder).filter(
            IndexFolder.status == "pending",
            IndexFolder.created_at <= latest_full_run.stopped_at,
        ).update(
            {
                "status": "completed",
                "updated_at": now or datetime.utcnow(),
            },
            synchronize_session=False,
        )

    def _set_folder_statuses(
        self,
        db: Session,
        folder_ids: Set[int],
        status: str,
        now: Optional[datetime] = None,
    ):
        if not folder_ids:
            return
        db.query(IndexFolder).filter(
            IndexFolder.id.in_(folder_ids),
        ).update(
            {
                "status": status,
                "updated_at": now or datetime.utcnow(),
            },
            synchronize_session=False,
        )

    def _finalize_folder_statuses(
        self,
        db: Session,
        folder_ids: Set[int],
        run_status: str,
        now: datetime,
    ):
        folder_status = {
            "completed": "completed",
            "stopped": "stopped",
            "failed": "failed",
        }.get(run_status)
        if folder_status:
            self._set_folder_statuses(db, folder_ids, folder_status, now)

    def get_status(self, db: Session) -> Dict[str, Any]:
        self._reconcile_abandoned_runs(db)
        run_id = self.current_run_id
        run = db.get(IndexRun, run_id) if run_id else db.query(IndexRun).order_by(IndexRun.id.desc()).first()
        if not run:
            return self._empty_status()

        discovered = run.discovered_files if run.discovered_files is not None else (run.total_files or 0)
        # Old terminal rows are backfilled by upgrade_schema; a stopped new
        # run intentionally remains indeterminate because discovery did not
        # finish.
        discovery_complete = bool(run.discovery_complete)
        processed = run.processed_files if run.processed_files is not None else (
            (run.indexed_files or 0) + (run.skipped_files or 0) + (run.failed_files or 0)
        )
        progress = None
        if discovery_complete:
            progress = (processed / discovered * 100.0) if discovered else 100.0

        status_str = "STOPPING" if self.is_stopping and run.status == "running" else run.status.upper()
        return {
            "status": status_str,
            "run_id": run.id,
            # Keep total_files for old clients while exposing the new fields.
            "total_files": run.total_files if run.total_files is not None else discovered,
            "discovered_files": discovered,
            "discovery_complete": discovery_complete,
            "processed_files": processed,
            "indexed_files": run.indexed_files or 0,
            "skipped_files": run.skipped_files or 0,
            "failed_files": run.failed_files or 0,
            "deleted_files": run.deleted_files or 0,
            "details_complete": bool(run.details_complete),
            "detail_rows_retained": run.detail_rows_retained or 0,
            "progress_percentage": round(progress, 1) if progress is not None else None,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "stopped_at": run.stopped_at.isoformat() if run.stopped_at else None,
        }

    def start_run(
        self,
        changed_xml_path: Optional[str] = None,
        deleted_xml_path: Optional[str] = None,
    ) -> int:
        with self._state_lock:
            if self.is_running or self.is_stopping:
                raise RuntimeError("An indexing run is already in progress")
            self.stop_event.clear()
            self._failure_event.clear()
            self.is_running = True
            self.is_stopping = False

        db = SessionLocal()
        try:
            with db_write_lock:
                config = get_config(db)
                now = datetime.utcnow()
                self._reconcile_abandoned_runs(db, now)
                self._reconcile_legacy_folder_statuses(db, now)
                # A null lease is treated as active for backward compatibility
                # with rows created before lease metadata existed.
                active_run = db.query(IndexRun).filter(
                    IndexRun.status == "running",
                    (IndexRun.lease_expires_at.is_(None) | (IndexRun.lease_expires_at >= now)),
                ).first()
                if active_run:
                    raise RuntimeError("An indexing run is already active")

                lease_owner = uuid.uuid4().hex
                self._lease_owner = lease_owner
                self._lease_duration_seconds = max(60.0, config.worker_shutdown_timeout_seconds * 4)
                xml_cfg = db.query(IncrementalXmlConfig).filter_by(id=1).first()
                if not xml_cfg:
                    xml_cfg = IncrementalXmlConfig(id=1)
                    db.add(xml_cfg)
                if changed_xml_path is not None:
                    xml_cfg.changed_xml_path = changed_xml_path
                if deleted_xml_path is not None:
                    xml_cfg.deleted_xml_path = deleted_xml_path
                db.commit()

                run = IndexRun(
                    status="running",
                    changed_xml_path=xml_cfg.changed_xml_path,
                    deleted_xml_path=xml_cfg.deleted_xml_path,
                    total_files=0,
                    discovered_files=0,
                    processed_files=0,
                    discovery_complete=False,
                    details_complete=True,
                    detail_rows_retained=0,
                    lease_owner=lease_owner,
                    lease_expires_at=now + timedelta(seconds=self._lease_duration_seconds),
                )
                db.add(run)
                db.commit()
                db.refresh(run)
                self.current_run_id = run.id
                with self._detail_lock:
                    self._detail_counts[run.id] = 0
                    self._detail_capped.discard(run.id)

                self._thread = threading.Thread(
                    target=self._execute_run,
                    args=(run.id, xml_cfg.changed_xml_path, xml_cfg.deleted_xml_path),
                    daemon=True,
                    name=f"index-run-{run.id}",
                )
                self._thread.start()
                self._start_lease_renewal(run.id, lease_owner)
                return run.id
        except Exception:
            self._lease_owner = None
            with self._state_lock:
                self.is_running = False
            raise
        finally:
            db.close()

    def stop_run(self):
        with self._state_lock:
            if not self.is_running:
                return
            self.is_stopping = True
            self.stop_event.set()

    def _start_lease_renewal(self, run_id: int, owner: str):
        self._lease_stop.clear()

        def renew():
            interval = max(5.0, self._lease_duration_seconds / 3)
            while not self._lease_stop.wait(interval):
                db = SessionLocal()
                try:
                    expires = datetime.utcnow() + timedelta(seconds=self._lease_duration_seconds)
                    with db_write_lock:
                        db.query(IndexRun).filter(
                            IndexRun.id == run_id,
                            IndexRun.lease_owner == owner,
                            IndexRun.status == "running",
                        ).update({"lease_expires_at": expires}, synchronize_session=False)
                        db.commit()
                except Exception as exc:
                    get_logger(run_id=run_id).error("Could not renew index run lease: %s", exc)
                    db.rollback()
                finally:
                    db.close()

        self._lease_thread = threading.Thread(
            target=renew,
            daemon=True,
            name=f"index-lease-{run_id}",
        )
        self._lease_thread.start()

    def _stop_lease_renewal(self):
        self._lease_stop.set()
        if self._lease_thread and self._lease_thread is not threading.current_thread():
            self._lease_thread.join(timeout=2)
        self._lease_thread = None
        self._lease_owner = None

    def _flush_counters(self, run_id: int, batch: CounterBatch):
        if not batch.values:
            return
        db = SessionLocal()
        try:
            column_names = {
                "discovered": "discovered_files",
                "processed": "processed_files",
                "indexed": "indexed_files",
                "skipped": "skipped_files",
                "failed": "failed_files",
            }
            expressions = {
                column_names.get(key, key): getattr(IndexRun, column_names.get(key, key)) + value
                for key, value in batch.values.items()
                if value
            }
            if expressions:
                with db_write_lock:
                    db.query(IndexRun).filter(IndexRun.id == run_id).update(
                        expressions, synchronize_session=False
                    )
                    db.commit()
                    batch.clear()
        finally:
            db.close()

    def _flush_when_due(self, run_id: int, batch: CounterBatch, config: Any):
        if (
            batch.terminal_count >= config.counter_flush_interval
            or time.monotonic() - batch.last_flush >= 1.0
        ):
            self._flush_counters(run_id, batch)

    def _set_discovery_complete(self, run_id: int, complete: bool):
        db = SessionLocal()
        try:
            with db_write_lock:
                db.query(IndexRun).filter(IndexRun.id == run_id).update(
                    {"discovery_complete": bool(complete)}, synchronize_session=False
                )
                db.commit()
        finally:
            db.close()

    def _record_detail(
        self,
        run_id: int,
        file_path: str,
        status: str,
        error_message: Optional[str] = None,
        chunks_indexed: int = 0,
    ):
        """Retain only a bounded sample of per-file diagnostics."""
        with self._detail_lock:
            count = self._detail_counts.get(run_id, 0)
            if count >= self.DETAIL_ROW_LIMIT:
                if run_id in self._detail_capped:
                    return
                self._detail_capped.add(run_id)
                db = SessionLocal()
                try:
                    with db_write_lock:
                        db.query(IndexRun).filter(IndexRun.id == run_id).update(
                            {"details_complete": False}, synchronize_session=False
                        )
                        db.commit()
                finally:
                    db.close()
                return
            self._detail_counts[run_id] = count + 1

        db = SessionLocal()
        try:
            with db_write_lock:
                db.add(IndexRunFile(
                    run_id=run_id,
                    file_path=file_path,
                    status=status,
                    chunks_indexed=chunks_indexed,
                    error_message=error_message,
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow(),
                ))
                db.query(IndexRun).filter(IndexRun.id == run_id).update(
                    {"detail_rows_retained": IndexRun.detail_rows_retained + 1},
                    synchronize_session=False,
                )
                db.commit()
        finally:
            db.close()

    def _producer(
        self,
        run_id: int,
        db_factory,
        file_queue: queue.Queue,
        changed_paths: Set[str],
        deleted_paths: Set[str],
        config: Any = None,
        folder_paths: Optional[Set[str]] = None,
        changed_file_paths: Optional[Dict[str, str]] = None,
    ):
        db = None
        log = get_logger(run_id=run_id)
        counts = CounterBatch()
        discovery_succeeded = False
        try:
            db = db_factory()
            config = config or get_config(db)
            candidates = walk_folders_stream(
                db,
                self.stop_event,
                changed_paths,
                deleted_paths,
                folder_paths=folder_paths,
            )
            if changed_file_paths:
                incremental_items = iter_incremental_file_items(
                    db,
                    changed_file_paths,
                    deleted_paths,
                    self.stop_event,
                )
                candidates = chain(candidates, incremental_items)

            seen_paths = set()
            for item in candidates:
                if self.stop_event.is_set():
                    break
                canonical_path = item.get("canonical_path")
                if canonical_path in seen_paths:
                    continue
                seen_paths.add(canonical_path)
                counts.add(discovered=1)
                if item.get("status") == "skipped":
                    counts.add(skipped=1, processed=1)
                    self._record_detail(run_id, item["file_path"], "skipped", item.get("reason"))
                    self._flush_when_due(run_id, counts, config)
                    continue

                while not self.stop_event.is_set():
                    try:
                        file_queue.put(item, timeout=config.queue_put_timeout_seconds)
                        break
                    except queue.Full:
                        continue
                self._flush_when_due(run_id, counts, config)
            discovery_succeeded = not self.stop_event.is_set() and not self._failure_event.is_set()
        except Exception as exc:
            self._failure_event.set()
            self.stop_event.set()
            log.error("Producer failed: %s", exc, exc_info=True)
        finally:
            try:
                self._flush_counters(run_id, counts)
            except Exception as exc:
                self._failure_event.set()
                self.stop_event.set()
                log.error("Producer counter flush failed: %s", exc, exc_info=True)
            try:
                self._set_discovery_complete(run_id, discovery_succeeded and not self._failure_event.is_set())
            except Exception as exc:
                self._failure_event.set()
                self.stop_event.set()
                log.error("Could not persist discovery status: %s", exc, exc_info=True)
            finally:
                if db is not None:
                    db.close()

    def _consumer(
        self,
        run_id: int,
        db_factory,
        file_queue: queue.Queue,
        config: Any,
        converter_factory,
        embedder: Embedder,
        qdrant: Any,
    ):
        log = get_logger(run_id=run_id)
        counts = CounterBatch()
        db = None
        try:
            db = db_factory()
            converter = converter_factory()
            while True:
                try:
                    item = file_queue.get(timeout=config.queue_put_timeout_seconds)
                except queue.Empty:
                    continue
                try:
                    if item is None:
                        return
                    if self.stop_event.is_set():
                        continue
                    self._process_item(run_id, item, db, config, converter, embedder, qdrant, counts, log)
                    self._flush_when_due(run_id, counts, config)
                except RunStopped:
                    # Stopping a file before it reaches a terminal state is
                    # intentionally not counted as failed or processed.
                    continue
                except Exception as exc:
                    self._failure_event.set()
                    self.stop_event.set()
                    log.error("Worker failed: %s", exc, exc_info=True)
                    # Continue draining so the coordinator can always place
                    # sentinels and join every consumer.
                finally:
                    db.rollback()
                    file_queue.task_done()
        except Exception as exc:
            self._failure_event.set()
            self.stop_event.set()
            log.error("Worker exited unexpectedly: %s", exc, exc_info=True)
        finally:
            try:
                self._flush_counters(run_id, counts)
            except Exception as exc:
                self._failure_event.set()
                self.stop_event.set()
                log.error("Worker counter flush failed: %s", exc, exc_info=True)
            finally:
                if db is not None:
                    db.close()

    def _process_item(
        self,
        run_id: int,
        item: Dict[str, Any],
        db: Session,
        config: Any,
        converter: DocumentConverter,
        embedder: Embedder,
        qdrant: Any,
        counts: CounterBatch,
        log: Any,
    ):
        file_path = normalize_file_path(item["file_path"])
        file_name = item.get("file_name") or os.path.basename(file_path)
        extension = item.get("extension") or os.path.splitext(file_name)[1].lower()
        wrote_points = False
        try:
            if self.stop_event.is_set():
                raise RunStopped()
            if not item.get("force_reindex") and is_already_indexed(
                qdrant, config.collection_name, file_path, config.qdrant_timeout_seconds
            ):
                counts.add(skipped=1, processed=1)
                self._record_detail(run_id, file_path, "skipped", "Already indexed in Qdrant")
                return

            chunker = get_chunker(extension, db, config)
            if not chunker:
                counts.add(skipped=1, processed=1)
                self._record_detail(run_id, file_path, "skipped", "No matching chunker configured")
                return

            if item.get("force_reindex"):
                delete_points_by_file_path(
                    qdrant, config.collection_name, file_path,
                    timeout=config.qdrant_timeout_seconds, raise_errors=True,
                )

            markdown = converter.convert(file_path)
            if self.stop_event.is_set():
                raise RunStopped()
            classification = classify_file(file_path, db)
            index_roots = item.get("index_roots") or get_index_roots(db, file_path)
            indexed_at = datetime.utcnow().isoformat()
            point_count = 0
            saw_chunk = False
            if hasattr(chunker, "iter_chunk_batches"):
                batches = chunker.iter_chunk_batches(
                    markdown,
                    file_name,
                    config.embedding_batch_size,
                    max_chunk_chars=config.max_chunk_chars,
                )
            else:
                # Compatibility for third-party chunkers predating the lazy
                # interface.  Built-in chunkers always take the bounded path.
                chunks = chunker.chunk(markdown, file_name)
                if any(len(chunk.text) > config.max_chunk_chars for chunk in chunks):
                    raise ValueError("A chunk exceeds max_chunk_chars")
                batches = (
                    chunks[index:index + config.embedding_batch_size]
                    for index in range(0, len(chunks), config.embedding_batch_size)
                )
            for chunk_batch in batches:
                saw_chunk = True
                if self.stop_event.is_set():
                    raise RunStopped()
                vectors = embedder.embed_batch([chunk.text for chunk in chunk_batch])
                if len(vectors) != len(chunk_batch):
                    raise ValueError("Embedder returned a different number of vectors than chunks")
                for point_batch in iter_point_batches(
                    file_path,
                    chunk_batch,
                    vectors,
                    classification=classification,
                    max_points=config.qdrant_upsert_batch_size,
                    max_bytes=config.qdrant_upsert_max_bytes,
                    file_name=file_name,
                    extension=extension,
                    indexed_at=indexed_at,
                    index_roots=index_roots,
                ):
                    if self.stop_event.is_set():
                        raise RunStopped()
                    upsert_point_batch(
                        qdrant,
                        config.collection_name,
                        point_batch,
                        wait=True,
                        timeout=config.qdrant_timeout_seconds,
                    )
                    wrote_points = True
                    point_count += len(point_batch)

            if not saw_chunk or point_count == 0:
                counts.add(skipped=1, processed=1)
                self._record_detail(run_id, file_path, "skipped", "Chunker returned 0 chunks")
                return
            if self.stop_event.is_set():
                raise RunStopped()

            counts.add(indexed=1, processed=1)
            self._record_detail(run_id, file_path, "completed", chunks_indexed=point_count)
            log.info("Successfully indexed %s (%d chunks)", file_name, point_count)
        except RunStopped:
            if wrote_points:
                delete_points_by_file_path(
                    qdrant, config.collection_name, file_path,
                    timeout=config.qdrant_timeout_seconds,
                )
            raise
        except (EmptyContentError, FileSizeLimitError, UnsupportedFileTypeError) as exc:
            delete_points_by_file_path(
                qdrant,
                config.collection_name,
                file_path,
                timeout=config.qdrant_timeout_seconds,
            )
            counts.add(skipped=1, processed=1)
            self._record_detail(run_id, file_path, "skipped", str(exc))
            log.info("Skipped %s: %s", file_path, exc)
        except Exception as exc:
            # A known failure must not leave a path that looks indexed on the
            # next run.  Cleanup is best-effort because the original failure
            # should remain visible in the run outcome.
            delete_points_by_file_path(
                qdrant, config.collection_name, file_path,
                timeout=config.qdrant_timeout_seconds,
            )
            self._failure_event.set()
            counts.add(failed=1, processed=1)
            self._record_detail(run_id, file_path, "failed", str(exc))
            log.error("Failed processing %s: %s", file_path, exc)

    def _process_single_file(
        self,
        run_id: int,
        file_path: str,
        config: Any,
        converter: DocumentConverter,
        embedder: Embedder,
        qdrant: Any,
    ):
        """Compatibility entry point for integrations using the old worker API."""
        db = SessionLocal()
        counts = CounterBatch()
        try:
            normalized = normalize_file_path(file_path)
            item = {
                "file_path": normalized,
                "file_name": os.path.basename(normalized),
                "extension": os.path.splitext(normalized)[1].lower(),
                "index_roots": get_index_roots(db, normalized),
                "force_reindex": False,
            }
            self._process_item(
                run_id, item, db, config, converter, embedder, qdrant,
                counts, get_logger(run_id=run_id, file_path=normalized),
            )
            self._flush_counters(run_id, counts)
        finally:
            db.close()

    def _rollback_file(self, db: Session, run_file: IndexRunFile, qdrant: Any, collection_name: str):
        """Legacy cleanup helper retained for callers of the former pipeline."""
        delete_points_by_file_path(qdrant, collection_name, run_file.file_path)
        run_file.status = "pending"
        with db_write_lock:
            db.commit()

    def _send_sentinels(self, file_queue: queue.Queue, count: int, timeout: float):
        for _ in range(count):
            while True:
                try:
                    file_queue.put(None, timeout=timeout)
                    break
                except queue.Full:
                    # Consumers are expected to keep draining even after a
                    # stop signal, so this remains interruptible.
                    if not any(thread.is_alive() for thread in getattr(self, "_consumer_threads", [])):
                        return

    def _wait_for_producer(self, producer, shutdown_timeout: float) -> bool:
        """Wait for discovery without applying a shutdown limit to normal scans."""
        deadline = None
        while producer.is_alive():
            if self.stop_event.is_set():
                if deadline is None:
                    deadline = time.monotonic() + shutdown_timeout
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                producer.join(timeout=min(0.25, remaining))
            else:
                producer.join(timeout=0.25)
        return True

    def _start_reaper(
        self,
        run_id: int,
        producer,
        consumers,
        qdrant: Any,
        folder_ids: Optional[Set[int]] = None,
        file_queue: Optional[queue.Queue] = None,
        put_timeout: float = 0.25,
    ):
        """Finalize a run only after timed-out worker threads have exited."""
        def reap():
            producer.join()
            if file_queue is not None:
                self._send_sentinels(file_queue, len(consumers), put_timeout)
            for thread in consumers:
                thread.join()
            db = SessionLocal()
            try:
                with db_write_lock:
                    run = db.get(IndexRun, run_id)
                    if run:
                        run.total_files = run.discovered_files or 0
                        if self._failure_event.is_set():
                            run.status = "failed"
                        elif self.stop_event.is_set():
                            run.status = "stopped"
                        else:
                            run.status = "completed"
                        stopped_at = datetime.utcnow()
                        run.stopped_at = stopped_at
                        self._finalize_folder_statuses(
                            db,
                            folder_ids or set(),
                            run.status,
                            stopped_at,
                        )
                        db.commit()
            finally:
                db.close()
                if qdrant is not None and hasattr(qdrant, "close"):
                    qdrant.close()
                self._stop_lease_renewal()
                with self._state_lock:
                    self.is_running = False
                    self.is_stopping = False

        threading.Thread(
            target=reap,
            daemon=True,
            name=f"index-reaper-{run_id}",
        ).start()

    def _execute_run(self, run_id: int, changed_xml: Optional[str], deleted_xml: Optional[str]):
        db = SessionLocal()
        log = get_logger(run_id=run_id)
        producer = None
        consumers = []
        qdrant = None
        scan_folder_ids: Set[int] = set()
        scan_folder_paths: Set[str] = set()
        threads_alive = False
        try:
            config = get_config(db)
            log.info(
                "Starting index run %s (workers=%d queue=%d embed_batch=%d qdrant_batch=%d)",
                run_id,
                config.index_workers,
                config.index_queue_capacity,
                config.embedding_batch_size,
                config.qdrant_upsert_batch_size,
            )
            scan_folders = (
                db.query(IndexFolder)
                .filter(IndexFolder.status.in_(self.SCAN_FOLDER_STATUSES))
                .all()
            )
            scan_folder_ids = {folder.id for folder in scan_folders}
            scan_folder_paths = {folder.path for folder in scan_folders}
            self._set_folder_statuses(db, scan_folder_ids, "indexing")
            db.commit()

            qdrant = get_qdrant_client(host=config.qdrant_host, port=config.qdrant_port)
            ensure_collection(qdrant, config.collection_name, config.embedding_dimensions)

            changed_paths, deleted_paths, xml_paths = parse_incremental_inputs(changed_xml, deleted_xml)
            changed_file_paths = {
                key: xml_paths[key]
                for key in changed_paths
            }
            # Changed paths are replacements too; deleted paths win conflicts.
            paths_to_delete = deleted_paths | changed_paths
            deleted_count = 0
            for key in paths_to_delete:
                delete_points_by_file_path(
                    qdrant,
                    config.collection_name,
                    xml_paths[key],
                    timeout=config.qdrant_timeout_seconds,
                    raise_errors=True,
                )
                if key in deleted_paths:
                    deleted_count += 1
            with db_write_lock:
                db.query(IndexRun).filter(IndexRun.id == run_id).update(
                    {"deleted_files": deleted_count}, synchronize_session=False
                )
                db.commit()

            file_queue = queue.Queue(maxsize=config.index_queue_capacity)
            embedder = Embedder(
                model_name=config.embedding_model,
                dimensions=config.embedding_dimensions,
                embedding_concurrency=config.embedding_concurrency,
                max_batch_size=config.embedding_batch_size,
            )
            producer = threading.Thread(
                target=self._producer,
                args=(
                    run_id,
                    SessionLocal,
                    file_queue,
                    changed_paths,
                    deleted_paths,
                    config,
                    scan_folder_paths,
                    changed_file_paths,
                ),
                daemon=True,
                name=f"index-producer-{run_id}",
            )
            producer.start()

            def converter_factory():
                return DocumentConverter(
                    max_file_size_mb=config.max_file_size_mb,
                    max_markdown_chars=config.max_markdown_chars,
                    conversion_timeout_seconds=config.conversion_timeout_seconds,
                )

            self._consumer_threads = []
            for worker_number in range(max(1, config.index_workers)):
                worker = threading.Thread(
                    target=self._consumer,
                    args=(run_id, SessionLocal, file_queue, config, converter_factory, embedder, qdrant),
                    daemon=True,
                    name=f"index-worker-{run_id}-{worker_number}",
                )
                worker.start()
                consumers.append(worker)
                self._consumer_threads.append(worker)

            if not self._wait_for_producer(producer, config.worker_shutdown_timeout_seconds):
                self._failure_event.set()
                self.stop_event.set()
                log.error("Producer did not stop before the shutdown timeout")
                producer.join(timeout=config.worker_shutdown_timeout_seconds)

            if not producer.is_alive():
                self._send_sentinels(file_queue, len(consumers), config.queue_put_timeout_seconds)
            for worker in consumers:
                worker.join(timeout=config.worker_shutdown_timeout_seconds)

            all_exited = not producer.is_alive() and not any(worker.is_alive() for worker in consumers)
            all_threads = [producer, *consumers]
            with db_write_lock:
                run = db.get(IndexRun, run_id)
                if run and all_exited:
                    discovered = run.discovered_files or 0
                    run.total_files = discovered
                    if self._failure_event.is_set():
                        run.status = "failed"
                    elif self.stop_event.is_set():
                        run.status = "stopped"
                    else:
                        run.status = "completed"
                    stopped_at = datetime.utcnow()
                    run.stopped_at = stopped_at
                    self._finalize_folder_statuses(
                        db,
                        scan_folder_ids,
                        run.status,
                        stopped_at,
                    )
                    db.commit()
                elif run:
                    # Keep the row non-terminal while a thread could still write.
                    run.status = "running"
                    db.commit()
                    self._start_reaper(
                        run_id, producer, consumers, qdrant,
                        folder_ids=scan_folder_ids,
                        file_queue=file_queue if producer.is_alive() else None,
                        put_timeout=config.queue_put_timeout_seconds,
                    )
        except Exception as exc:
            self._failure_event.set()
            self.stop_event.set()
            log.error("Run %s failed: %s", run_id, exc, exc_info=True)
            all_threads = [thread for thread in [producer, *consumers] if thread]
            with db_write_lock:
                run = db.get(IndexRun, run_id)
                if run and not any(thread.is_alive() for thread in all_threads):
                    run.status = "failed"
                    stopped_at = datetime.utcnow()
                    run.stopped_at = stopped_at
                    self._finalize_folder_statuses(
                        db,
                        scan_folder_ids,
                        run.status,
                        stopped_at,
                    )
                    db.commit()
                elif run:
                    self._start_reaper(
                        run_id, producer, consumers, qdrant,
                        folder_ids=scan_folder_ids,
                        file_queue=file_queue if "file_queue" in locals() and producer.is_alive() else None,
                        put_timeout=(config.queue_put_timeout_seconds if "config" in locals() else 0.25),
                    )
        finally:
            try:
                threads_alive = any(thread.is_alive() for thread in [producer, *consumers] if thread)
                if not threads_alive and qdrant is not None and hasattr(qdrant, "close"):
                    qdrant.close()
            finally:
                db.close()
                with self._state_lock:
                    if not threads_alive:
                        self._stop_lease_renewal()
                        self.is_running = False
                        self.is_stopping = False


indexer_runner = IndexerRunner()
