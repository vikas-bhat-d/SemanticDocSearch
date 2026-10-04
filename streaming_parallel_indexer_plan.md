# Streaming Parallel Indexer — Refactor Plan

> **Goal:** Bound memory and work at every indexing stage: discover files lazily, keep only a limited number of files in flight, emit chunks incrementally, embed chunks in bounded batches, and upsert bounded point batches to Qdrant. Preserve run-level stop/restart behavior and strictly bound new per-run detail while retaining historical run details until a safe retention strategy is in place. Qdrant stores vectors and is queried by normalized file path for skip decisions; this plan does not add a manifest or file fingerprinting. The path-based skip rule is intentionally presence-based and does not guarantee detection of an abruptly interrupted partial write.

> **Review status (2026-10-03):** The original proposal does not fix the main memory issue. Its consumer still materializes every chunk, every embedding, and every Qdrant point for one document, then calls `upsert_file_chunks()` once with the entire document. It also proposes dropping historical per-file rows, trusts any matching Qdrant point as proof of a complete index, and leaves deleted XML entries eligible for rediscovery. The corrections below are part of the plan, not optional follow-up cleanup.

---

## Table of Contents

1. [Current Architecture Problems](#1-current-architecture-problems)
2. [Target Architecture](#2-target-architecture)
3. [Data Flow Diagram](#3-data-flow-diagram)
4. [Files to Change](#4-files-to-change)
5. [Step-by-Step Implementation Plan](#5-step-by-step-implementation-plan)
6. [SQLite Schema Changes](#6-sqlite-schema-changes)
7. [Qdrant Query Strategy (skip logic)](#7-qdrant-query-strategy-skip-logic)
8. [Progress Tracking Without Total Count](#8-progress-tracking-without-total-count)
9. [Stop Signal Handling — Full Detail](#9-stop-signal-handling--full-detail)
10. [Incremental XML Handling](#10-incremental-xml-handling)
11. [Backward Compatibility Notes](#11-backward-compatibility-notes)
12. [Tests to Update/Add](#12-tests-to-updateadd)
13. [Implementation Order](#13-implementation-order)
14. [UI Changes Required](#14-ui-changes-required)
15. [Additional Large-Corpus Code Audit](#15-additional-large-corpus-code-audit)
16. [Resource Limits and Defaults](#16-resource-limits-and-defaults)
17. [Rollout and Acceptance Criteria](#17-rollout-and-acceptance-criteria)

---

## 1. Current Architecture Problems

### Problem A — Full discovery before any indexing

```
runner._execute_run():
  Step 1: walk_folders() -> collects ALL files -> list files_to_process   <- blocks everything
  Step 2: ThreadPoolExecutor.submit(all files at once)
```

On a folder with 50,000 files this means **zero** indexing starts until the entire walk is done. On network shares this can take minutes.

### Problem B — File path stored in SQLite `IndexRunFile`

`IndexRunFile.file_path` is populated for every file on every run, including unchanged/skipped files. This creates avoidable per-run row growth and makes historical run details a poor source for current file state. Keep run history for audit/API compatibility, but do not add another current-state table. Qdrant is the source for the simple file-exists skip check.

### Problem C — Traverser coupled to Qdrant check

`walk_folders()` currently calls `check_file_exists_and_unchanged()` (a Qdrant scroll) **inline** per file, serializing discovery behind network calls. Keep discovery filesystem-only and perform one bounded Qdrant lookup by `file_path` in the worker after dequeueing. The per-file request is intentional in this simpler design.

### Problem D — The proposed plan still materializes a whole document's embeddings and points

`Embedder.embed_batch()` calls `model.encode(..., batch_size=32)`, but that `batch_size` only limits the model's internal forward pass. It still returns a vector for every supplied text. The original plan supplied every chunk in a file at once, constructed a second full `points` list, then called `upsert_file_chunks()` once. That function built another list of `PointStruct` values and sent the entire file in one Qdrant request. A file with many chunks can therefore exhaust RAM or exceed request limits even after file discovery is streamed.

### Problem E — A bounded file queue does not bound document memory

Each consumer still holds `md_text`, a full `chunks` list, a full `vectors` list, and a full `points` list. With four consumers, four large documents can be resident at once. `DocumentConverter.convert()` returns the entire MarkItDown output as a string; the current 100 MB source-file limit does not bound expanded markdown size. Chunkers also build lists and intermediate split/row lists.

### Problem F — Qdrant state cannot prove a file is complete

The simplified skip query checks for any point matching `file_path` with `limit=1`; it does not compute timestamps or hashes. This is intentionally presence-based: a matching path is treated as already indexed unless the path is explicitly forced by incremental XML. Use deterministic point IDs and bounded cleanup on known failures, but do not add a manifest or a generation-publication protocol for this concern.

### Problem G — Incremental XML and current indexing flow disagree on deletion

The runner deletes vectors for `FILE` entries and then traverses every configured folder. If a path from `deleted_paths.xml` still exists on disk, traversal finds it and reindexes it in the same run. Deleted paths must be excluded from discovery for that run. Changed paths must be forced for reindexing; duplicate paths must be normalized and de-duplicated, with deleted taking precedence if a path appears in both lists.

### Problem H — More large-corpus hotspots

- One Qdrant file-path lookup is made for every candidate that is not explicitly forced. This is an accepted network cost for the simpler skip strategy; keep it out of the producer so directory discovery can continue while workers perform lookups.
- `_execute_run()` submits a `Future` for every candidate after storing all paths in `files_to_process`; this makes both Python objects and executor work unbounded.
- The producer sketch commits a SQLite counter update for every discovered file. That creates avoidable write contention and slows discovery.
- The proposal shares one `DocumentConverter` across consumer threads without establishing that its MarkItDown object is thread-safe. Concurrent conversion and embedding worker counts also need independent limits.
- `update_payload_for_file()` scrolls only the first 500 Qdrant points. Reclassifying a document with more than 500 chunks silently leaves old labels behind.
- `delete_points_by_file_path()` reports `1` for a successful delete request, regardless of how many chunks were removed, and hides errors as `0`; its return value is not a reliable number of deleted points or files.
- Dropping `index_run_files` at startup destroys historical run details and pending state. A migration must be additive, idempotent, backed up, and preserve the existing database.

---

## 2. Target Architecture

```
Start pressed
     |
     v
[IndexerRunner.start_run()]
     |  creates IndexRun row (no file rows upfront)
     |  spawns background thread: _execute_run()
     v
_execute_run()
 +-- Phase 0: Parse changed/deleted XML, delete tombstoned paths, build per-run sets
 +-- Phase 1: Launch PRODUCER thread
 |     +-- traverser.walk_folders_stream()
 |          - yields FileItem (canonical path, ext) or policy skip
 |          - does NOT call Qdrant (skip check happens in workers)
 |          - puts eligible item into bounded queue (configurable capacity)
 |          - respects stop_event
 |          - records discovery completion/error
 |
 +-- Phase 2: Run a fixed-size file worker pool (no submit-all futures)
 |     Each worker:
 |       1. pop item from queue
 |       2. query Qdrant for an existing point with the normalized file path unless forced
 |       3. convert within explicit per-file limits and stream chunks
 |       4. embed bounded chunk batches; build and upsert bounded point batches
 |       5. finish cleanup and update batched IndexRun counters
 |       7. loop until coordinator sends a sentinel after producer completion
 |
 +-- Phase 3: Join producer + consumers, mark run status
```

Discovery and processing overlap, but a bounded queue alone is insufficient: each worker must also use chunk, embedding, and Qdrant point batches. Do not add a manifest or fingerprinting layer. Keep `IndexRunFile` and its history during rollout; stop writing rows for ordinary unchanged/skipped files, keep bounded recent per-run detail, and retire old rows only through an explicit retention migration.

---

## 3. Data Flow Diagram

```
IndexFolder rows (SQLite)
        |
        v
  [PRODUCER thread]
  traverser.walk_folders_stream()
  * os.walk() per folder
  * apply exclusion filters (path/ext)
  * check enabled extensions
  * emit FileItem{path, canonical_path, ext, force_reindex}
        |  queue.put(item)  [bounded queue, backpressure built-in]
        v
  [ bounded Queue(maxsize = index_queue_capacity) ]
        |  queue.get()
        v
  [FILE worker thread 1..N]  (N = index_workers)
  +---------------------------------------------+
  | 1. Qdrant file_path existence check           |
  | 2. streamed/spooled conversion + lazy chunks |
  | 3. bounded embedding batch                   |
  | 4. deterministic point batch                 |
  | 5. bounded Qdrant upsert + acknowledged wait |
  | 6. update batched run counters                |
  +---------------------------------------------+
        |
        v
  Existing IndexRun history + Qdrant file chunks
```

---

## 4. Files to Change

| File | Change Type | Summary |
|---|---|---|
| `app/models.py` | **Additive schema** | Add discovery/terminal counters; preserve `IndexRunFile` during rollout |
| `app/indexer/runner.py` | **Refactor** | Bounded producer/worker pipeline; lifecycle-safe stop, failure, and per-file publication |
| `app/indexer/traverser.py` | **Refactor** | Remove Qdrant check; rename to `walk_folders_stream()`; add `stop_event` param |
| `app/indexer/chunker/*.py`, `chunker/base.py` | **Refactor** | Add iterator/batch interfaces so chunkers do not retain every chunk |
| `app/indexer/embedder.py` | **Refactor** | Provide bounded embedding batches and explicit memory/concurrency controls |
| `app/indexer/qdrant_ops.py` | **Refactor** | Add bounded `file_path` existence lookup, produce bounded point batches lazily, and send one bounded request at a time; deterministic IDs and wait/error handling |
| `app/indexer/converter.py` | **Harden** | Enforce source/output limits; isolate converter instances; use streaming/spooling or subprocess time/memory limits because an output-length check after conversion does not cap converter peak RAM |
| `app/routers/index.py` | **Update** | Preserve existing endpoints; expose discovery/completion/queue state accurately |
| `app/database.py`, `app/main.py` | **Migration** | Add versioned, idempotent, non-destructive migration with backup/recovery |
| `app/search/engine.py`, `app/routers/reclassify.py` | **Update** | Preserve bounded search and reclassify all points through paginated scroll |
| `tests/` | **Update** | Cover bounded batches, partial failures, recovery, XML precedence, cancellation, and scale |

---

## 5. Step-by-Step Implementation Plan

### Step 1 — Add bounded run counters; preserve run history

**What to do:**

1. Add `discovered_files`, `processed_files`, and `discovery_complete` to `IndexRun`; retain `total_files` for historical rows and API compatibility during migration.
3. Keep the `IndexRunFile` table and endpoint; never drop legacy rows during startup. For new runs, write only bounded detail (prioritize failures and a small recent/sample set), not one row per corpus file. Add `IndexRun.details_complete` and retained-count metadata so the API tells clients when details are partial. Retain/expire old rows only under a separately documented, backed-up policy.
4. Define the simple skip and force rules before coding: a non-forced file is skipped when a Qdrant point matches its normalized `file_path`; a path listed in changed XML is always reindexed. Do not compute or persist `mtime_ns`, file size, or SHA-256 fingerprints.

**New `IndexRun` model:**

```python
class IndexRun(Base):
    __tablename__ = "index_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=False, default="running")
    changed_xml_path = Column(Text, nullable=True)
    deleted_xml_path = Column(Text, nullable=True)
    discovered_files = Column(Integer, default=0)   # file paths presented to pipeline
    processed_files = Column(Integer, default=0)     # indexed + skipped + failed candidates
    discovery_complete = Column(Boolean, default=False)
    indexed_files = Column(Integer, default=0)
    skipped_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    deleted_files = Column(Integer, default=0)
    details_complete = Column(Boolean, default=True)  # false if per-file rows were capped
    detail_rows_retained = Column(Integer, default=0)
    # Keep total_files for old runs; stop using it as a live discovery counter.
```

> [!NOTE]
> Do not use `indexed / discovered` as a final progress measure while discovery continues. Report discovery and processed counts separately; only show a determinate percentage once producer discovery is complete.

---

### Step 2 — Add a versioned, non-destructive DB migration

Use a migration version table and explicit column/table existence checks. Make each migration transactional and idempotent. Never use `DROP TABLE index_run_files` as an automatic startup migration; it destroys run detail and pending rows. Take a verified copy of `data/config.db` before any schema migration that rewrites or retires existing data. Do not swallow arbitrary migration exceptions as “already applied”; detect the specific already-exists condition and fail startup on any other error.

---

### Step 3 — Call `upgrade_schema()` in `main.py` lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine, upgrade_schema
    upgrade_schema(engine)                        # apply versioned additive migrations
    Base.metadata.create_all(bind=engine)          # create missing tables
    seed_default_configs(SessionLocal())
    yield
```

> [!IMPORTANT]
> `create_all()` does not reconcile or remove obsolete tables. Migration logic must explicitly and safely create/add the required schema; startup must stop on migration failure instead of continuing with a half-upgraded database.

---

### Step 4 — Refactor `traverser.py`

**Remove:**
- The `qdrant_client` and `collection_name` parameters
- The `check_file_exists_and_unchanged()` call
- The Qdrant import

**Rename** `walk_folders` → `walk_folders_stream`

**New signature:**
```python
import threading

def walk_folders_stream(
    db: Session,
    stop_event: threading.Event,
    changed_paths: set[str],
    deleted_paths: set[str]
) -> Generator[Dict[str, Any], None, None]:
```

**Yields two kinds of items:**
```python
# Skipped (excluded/disabled extension/no chunker):
{"status": "skipped", "reason": "Excluded path", "file_path": fp}

# Candidate for indexing:
{"status": "pending", "file_path": fp, "canonical_path": key,
 "file_name": fname, "extension": ext, "force_reindex": key in changed_paths}
```

`file_path` is the normalized path used for I/O and the Qdrant payload lookup; `canonical_path` is used only for XML comparison and de-duplication (case-normalized on Windows). Filter `deleted_paths` before queueing. Force paths in `changed_paths` past the Qdrant existence check, but only if they are within a configured root and pass normal exclusion/file-type rules. De-duplicate and remove nested/overlapping configured roots before walking so a corpus-sized `seen_paths` set is not needed. If distinct traversal aliases still need suppression, use a temporary SQLite table with a unique canonical path, not an in-memory set proportional to corpus size. `os.walk()` still materializes one directory's `dirs` and `files` lists; if single-directory sizes can be very large, use an explicit `os.scandir()` traversal stack or record/measure that per-directory memory bound.

**Stop event check** inside the `for file_name in files` loop:
```python
if stop_event.is_set():
    return
```

> [!IMPORTANT]
> The traverser no longer performs Qdrant I/O. It is a filesystem walker + filter; the worker performs the Qdrant `file_path` lookup after dequeueing.

---

### Step 5 — Rewrite `runner.py`

This is the core change. The full `_execute_run` is replaced with a producer–consumer model.

#### 5a. New state on `IndexerRunner`

```python
class IndexerRunner:
    def __init__(self):
        self.stop_event = threading.Event()
        self.is_running = False
        self.is_stopping = False
        self.current_run_id: Optional[int] = None
        self._thread: Optional[threading.Thread] = None
```

#### 5b. Counter writes — batch them

Keep atomic SQL increments for counters updated by multiple workers, but accumulate deltas locally and persist at a bounded interval (for example every 25 terminal files or once per second). Do not open and commit a SQLite session for every discovered file. Never silently swallow a counter write failure; log it and fail or reconcile counters from retained per-file outcomes before marking the run complete.

#### 5c. Producer function

```python
def _producer(
    self,
    run_id: int,
    db_factory,
    file_queue: queue.Queue,
    changed_paths: set[str],
    deleted_paths: set[str]
):
    """
    Walks all indexed folders and pushes FileItems into file_queue.
    The coordinator owns worker shutdown and sentinel delivery.
    """
    db = db_factory()
    log = get_logger(run_id=run_id)
    local_counts = new_local_counter_batch()
    discovery_succeeded = False
    try:
        for item in walk_folders_stream(db, self.stop_event, changed_paths, deleted_paths):
            if self.stop_event.is_set():
                break
            if item["status"] == "skipped":
                # Count file-level policy skips as discovered + terminal work.
                local_counts.add(discovered=1, skipped=1, processed=1)
                flush_counts_when_due(run_id, local_counts)
                continue
            local_counts.add(discovered=1)
            flush_counts_when_due(run_id, local_counts)
            put_with_timeout_or_stop(file_queue, item, self.stop_event)
        discovery_succeeded = not self.stop_event.is_set()
    except Exception as e:
        log.error("Producer error: %s", e, exc_info=True)
        record_producer_failure(run_id, e)
        request_coordinated_shutdown()
    finally:
        flush_counts(run_id, local_counts)
        set_discovery_complete(run_id, complete=discovery_succeeded)
        db.close()
```

> [!NOTE]
> A bounded item count limits path metadata only. Also bound queued bytes, concurrent conversions, per-document text/chunk memory, embedding outputs, and Qdrant request bytes. Use timed queue operations so stop/failure cannot deadlock the producer.

#### 5d. Consumer function

```python
def _consumer(
    self,
    run_id: int,
    db_factory,
    file_queue: queue.Queue,
    config,
    converter_factory,
    embedder,
    qdrant
):
    """
    Pops FileItems and processes each file with bounded chunk, embedding,
    and Qdrant batches.
    """
    log = get_logger(run_id=run_id)
    db_local = db_factory()
    converter = converter_factory()  # one per worker unless thread safety is proven
    worker_counts = new_local_counter_batch()

    try:
        while True:
            item = file_queue.get()

            if item is None:  # SENTINEL
                file_queue.task_done()
                break

            if self.stop_event.is_set():
                file_queue.task_done()
                continue  # drain queue gracefully without processing

            fp = item.get("file_path", "<unknown>")
            try:
                fp = item["file_path"]
                ext = item["extension"]
                file_name = item["file_name"]
                if (not item["force_reindex"] and
                        qdrant_file_exists(
                            qdrant, config.collection_name, fp,
                            timeout=config.qdrant_timeout_seconds
                        )):
                    worker_counts.add(skipped=1, processed=1)
                    flush_counts_when_due(run_id, worker_counts)
                    continue

                chunker = get_chunker(ext, db_local, config)
                if not chunker:
                    worker_counts.add(skipped=1, processed=1)
                    flush_counts_when_due(run_id, worker_counts)
                    continue
                if item["force_reindex"]:
                    delete_points_by_file_path(
                        qdrant, config.collection_name, fp,
                        timeout=config.qdrant_timeout_seconds
                    )

                # A post-conversion length check bounds downstream work only;
                # converter peak memory needs streaming/spooling or process limits.
                md_text = converter.convert(fp)
                enforce_expanded_text_budget(md_text, config.max_markdown_chars)

                classification = classify_file(fp, db_local)
                point_count = 0
                for chunk_batch in chunker.iter_chunk_batches(md_text, file_name, config.embedding_batch_size):
                    if self.stop_event.is_set():
                        raise RunStopped()
                    vectors = embedder.embed_batch([chunk.text for chunk in chunk_batch])
                    for point_batch in iter_point_batches(
                        fp, chunk_batch, vectors, classification,
                        max_points=config.qdrant_upsert_batch_size,
                        max_bytes=config.qdrant_upsert_max_bytes
                    ):
                        upsert_point_batch(
                            qdrant, config.collection_name, point_batch, wait=True,
                            timeout=config.qdrant_timeout_seconds
                        )
                        point_count += len(point_batch)

                worker_counts.add(indexed=1, processed=1)
                flush_counts_when_due(run_id, worker_counts)
                log.info("Indexed %s (%d chunks)", file_name, point_count)

            except RunStopped:
                # A stopped/incomplete item is not counted as failed or processed.
                delete_points_by_file_path(
                    qdrant, config.collection_name, fp,
                    timeout=config.qdrant_timeout_seconds
                )
            except Exception as e:
                log.error("Failed %s: %s", fp, e)
                # Remove known partial writes so a later path-existence check
                # does not mistake a failed file for a complete index.
                delete_points_by_file_path(
                    qdrant, config.collection_name, fp,
                    timeout=config.qdrant_timeout_seconds
                )
                worker_counts.add(failed=1, processed=1)
                flush_counts_when_due(run_id, worker_counts)
        finally:
                file_queue.task_done()

    except Exception as e:
        record_worker_failure(run_id, e)
        request_coordinated_shutdown()
        log.error("Worker exited unexpectedly: %s", e, exc_info=True)
    finally:
        flush_counts(run_id, worker_counts)
        db_local.close()
```

#### 5e. `_execute_run()` orchestrator

```python
def _execute_run(self, run_id: int, changed_xml: Optional[str], deleted_xml: Optional[str]):
    db = SessionLocal()
    log = get_logger(run_id=run_id)
    log.info("Starting index run %s", run_id)
    producer_thread = None
    consumer_threads = []

    try:
        config = get_config(db)
        qdrant = get_qdrant_client(host=config.qdrant_host, port=config.qdrant_port)
        ensure_collection(qdrant, config.collection_name, config.embedding_dimensions)

        # Phase 0: Parse FILE entries once, normalize/deduplicate paths,
        # force changed paths, and suppress deleted paths for this whole run.
        # If a path is listed as both changed and deleted, deletion wins.
        changed_paths, deleted_paths = parse_incremental_inputs(changed_xml, deleted_xml)
        apply_deletions(qdrant, config.collection_name, deleted_paths)

        # Phase 1 + 2: Producer + Consumers
        num_workers = max(1, config.index_workers)
        file_queue = queue.Queue(maxsize=config.index_queue_capacity)

        embedder = Embedder(model_name=config.embedding_model, dimensions=config.embedding_dimensions)

        # Start producer thread
        producer_thread = threading.Thread(
            target=self._producer,
            args=(run_id, SessionLocal, file_queue, changed_paths, deleted_paths),
            daemon=False
        )
        producer_thread.start()

        # Start a fixed number of consumers; each owns its DB session and converter.
        consumer_threads = []
        for _ in range(num_workers):
            t = threading.Thread(
                target=self._consumer,
                args=(run_id, SessionLocal, file_queue, config,
                      lambda: DocumentConverter(max_file_size_mb=config.max_file_size_mb),
                      embedder, qdrant),
                daemon=False
            )
            t.start()
            consumer_threads.append(t)

        # Producer uses interruptible traversal and finite queue-put waits.
        producer_thread.join(timeout=config.worker_shutdown_timeout_seconds)
        if producer_thread.is_alive():
            request_coordinated_shutdown()
            producer_thread.join(timeout=config.worker_shutdown_timeout_seconds)

        # Only signal workers after the producer exited, so sentinels follow
        # every possible work item. Never release ownership if a thread survives.
        if not producer_thread.is_alive():
            signal_consumers_with_sentinels(
                file_queue, consumer_threads, self.stop_event,
                put_timeout=config.queue_put_timeout_seconds
            )
        for t in consumer_threads:
            t.join(timeout=config.worker_shutdown_timeout_seconds)

        if producer_thread.is_alive() or any(t.is_alive() for t in consumer_threads):
            persist_stopping_run_and_renewable_lease(run_id)
            register_run_reaper(run_id, producer_thread, consumer_threads)
            return  # Reaper finalizes only after every thread has exited.

        # Final status
        run = db.query(IndexRun).get(run_id)
        if producer_failed() or any_worker_failed():
            run.status = "failed"
            log.error("Run %s failed because a producer/worker did not finish cleanly", run_id)
        elif self.stop_event.is_set():
            run.status = "stopped"
            log.info("Run %s stopped by user", run_id)
        else:
            run.status = "completed"
            log.info("Run %s completed", run_id)
        run.stopped_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        log.error("Run %s failed: %s", run_id, e, exc_info=True)
        run = db.query(IndexRun).get(run_id)
        if run and not all_run_threads_exited(run_id):
            persist_stopping_run_and_renewable_lease(run_id)
            register_run_reaper(run_id, producer_thread, consumer_threads)
        elif run:
            run.status = "failed"
            run.stopped_at = datetime.utcnow()
            db.commit()
    finally:
        # The reaper owns release if any worker can still write. Do not let a
        # new run start while an old producer/consumer remains alive.
        if all_run_threads_exited(run_id):
            release_run_lease(run_id)
            self.is_running = False
            self.is_stopping = False
        db.close()
```

---

### Step 6 — Resume by rediscovery and Qdrant path state

Remove the special “latest stopped run” file replay. Each run re-walks configured roots; a non-forced file is skipped when the bounded Qdrant `file_path` lookup finds a point, and a path from changed XML is deleted and reindexed. Keep `IndexRunFile` rows for audit/API compatibility, but do not add a second file-state table. A known failure should delete that file's partial points before recording the failure; an abrupt process termination remains subject to the intentionally simple presence-based behavior.

---

### Step 7 — Update `get_status()` in `runner.py`

```python
def get_status(self, db: Session) -> Dict[str, Any]:
    run_id = self.current_run_id
    run = (db.query(IndexRun).get(run_id) if run_id
           else db.query(IndexRun).order_by(IndexRun.id.desc()).first())

    if not run:
        return {"status": "IDLE", "run_id": None, "discovered_files": 0,
                "indexed_files": 0, "skipped_files": 0, "failed_files": 0,
                "deleted_files": 0, "progress_percentage": 0.0}

    discovered = run.discovered_files or 0
    processed = run.processed_files or 0
    indexed = run.indexed_files or 0
    # Percentage is determinate only after producer discovery completes.
    if run.discovery_complete:
        prog = (processed / discovered * 100.0) if discovered else 100.0
    else:
        prog = None
    status_str = "STOPPING" if self.is_stopping else run.status.upper()

    return {
        "status": status_str,
        "run_id": run.id,
        "discovered_files": discovered,
        "discovery_complete": run.discovery_complete,
        "processed_files": processed,
        "indexed_files": indexed,
        "skipped_files": run.skipped_files or 0,
        "failed_files": run.failed_files or 0,
        "deleted_files": run.deleted_files or 0,
        "progress_percentage": round(prog, 1) if prog is not None else None,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "stopped_at": run.stopped_at.isoformat() if run.stopped_at else None
    }
```

---

### Step 8 — Update `routers/index.py`

1. Preserve the existing `/runs/{run_id}/files` endpoint during the compatibility window.
2. Add discovery-complete and processed counters while retaining `total_files` for older clients/history.
3. Do not use `IndexRunFile` as a corpus-wide current-state table; Qdrant `file_path` lookups handle the skip decision, while bounded `IndexRunFile` rows represent partial per-run diagnostics. Expose `details_complete` and retained count so clients never mistake a capped list for the whole corpus.

---

## 6. SQLite Schema Changes

Add, through versioned migrations:

- `index_runs.discovered_files`, `index_runs.processed_files`, `index_runs.discovery_complete`, and bounded-detail metadata as needed, preserving `total_files` values for old runs.
- Any indexes needed by the Qdrant `file_path` filter; do not add an `indexed_files` manifest table.
- Optional run-detail retention metadata; no automatic table drops.

Qdrant remains the source for the file-exists skip check. Existing `index_run_files` rows remain readable until a separate, backed-up retention migration is approved and implemented.

---

## 7. Qdrant Query Strategy (skip logic)

Use a bounded Qdrant payload lookup by normalized `file_path` as the skip check. Do not maintain a SQLite manifest and do not compute or persist file fingerprints:

```python
def is_already_indexed(qdrant, collection_name, file_path, timeout) -> bool:
    points, _ = qdrant.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(must=[
            FieldCondition(
                key="file_path",
                match=MatchValue(value=file_path),
            )
        ]),
        limit=1,
        with_payload=False,
        with_vectors=False,
        timeout=timeout,
    )
    return bool(points)
```

Run this lookup in a worker after the file leaves the bounded queue; the producer must remain filesystem-only. One request per candidate is an accepted tradeoff for avoiding manifest maintenance and repeated stat/hash work. A path listed in changed XML bypasses the lookup, deletes existing points for that path, and is reindexed. Files changed on disk without an explicit changed-XML entry are not detected automatically by this simplified strategy.

The lookup is intentionally presence-based: any matching point means the file is considered indexed. Deterministic point IDs and cleanup after known failures prevent duplicate writes and stale partial points where failure is observed. There is no legacy manifest backfill or full-collection cache/reconciliation step in this plan.

---

## 8. Progress Tracking Without Total Count

| Field | Meaning | Behavior |
|---|---|---|
| `discovered_files` | File paths presented by traverser, including explicit file-level policy skips | Grows while discovery runs |
| `indexed_files` | Files whose bounded point batches were written successfully | Grows as workers finish |
| `skipped_files` | Unchanged files and policy skips | Count once per unique path, not once per stage |
| `failed_files` | Files that failed conversion, chunking, embedding, or upsert | Count once per unique path |
| `processed_files` | Indexed + skipped + failed candidates | Grows as work reaches a terminal state |
| `progress_percentage` | `processed / discovered * 100` | Unknown/indeterminate until discovery completes |

**UI display:**
```
Discovered: 1,243  |  Indexed: 812  |  Skipped: 310  |  Failed: 2
Progress: 65.3%
```

While `discovery_complete` is false, show an indeterminate progress indicator and “Discovering files”; show the numeric ratio only after discovery ends. If discovery completes with zero candidates, report the run as complete with 100% progress (or display “No files found”) rather than divide by zero.

---

## 9. Stop Signal Handling — Full Detail

### 9a. What triggers a stop

The user clicks **Stop Indexing** on the dashboard → `POST /api/index/stop` → `indexer_runner.stop_run()` → `self.stop_event.set()`.

### 9b. Thread-by-thread behaviour

| Thread | When stop_event is set | Guaranteed action |
|---|---|---|
| **Producer** | Exits on stop, traversal error, or normal exhaustion; only normal exhaustion sets `discovery_complete=true` | Uses timeout-aware queue puts and checks worker health so a dead worker pool cannot strand discovery; does not enqueue sentinels |
| **Consumer (each)** | Checks stop before a file and between chunk batches | Uses `finally` for exactly-once `task_done()`; outer failure handling records the error and requests coordinated shutdown |
| **Coordinator** | Joins producer, signals live workers, then joins workers with finite timeouts | Persists `STOPPING`/lease ownership until all threads exit; never reports a terminal state while work can still write |

### 9c. Batched upsert and partial-file recovery

**Current behavior:** `upsert_file_chunks()` converts the entire `points_data` list into `PointStruct` objects and sends one request. The original proposed consumer also creates `chunks`, `vectors`, and `points` for the whole document before calling it. That does not solve the reported large-file problem.

**Required behavior:** The worker emits a bounded chunk batch, embeds it, creates at most one bounded point batch, and awaits Qdrant acknowledgement before releasing that memory and continuing. Enforce both a maximum point count and a serialized-byte budget; point text length varies, so a point count alone is not a sufficient request limit. Make point IDs deterministic from normalized file path and chunk index so a retried batch is idempotent.

```python
for chunk_batch in chunker.iter_chunk_batches(markdown, batch_size=embedding_batch_size):
    vectors = embedder.embed_batch([chunk.text for chunk in chunk_batch])
    for point_batch in iter_point_batches(fp, chunk_batch, vectors,
                                          max_points, max_serialized_bytes):
        qdrant_ops.upsert_point_batch(point_batch, wait=True, timeout=timeout)
```

The `embedding_batch_size` limits text and vector arrays retained by a worker; the Qdrant limits independently bound network request size. The current `SentenceTransformer.encode(batch_size=32)` only bounds model forward-pass microbatches; it does not bound the returned vector list. The caller must pass at most the configured chunk batch and must not collect all returned vectors. Build point batches incrementally from those vectors, include payload text and SDK serialization overhead in the memory/request budget, reject a single point that exceeds the byte cap, and retry only a finite number of times with deterministic IDs/backoff.

The skip decision remains the simple Qdrant `file_path` existence check described in section 7. Do not add staging generations, manifest pointers, timestamp comparisons, or hash validation just to support this batch loop. For an explicitly forced path, delete its existing points before writing the replacement. If a failure is observed after one or more writes, delete all points for that path before recording the failure so the next run can retry.

> [!WARNING]
> A Qdrant timeout does not prove that the batch was not written. Deterministic IDs make retries safe when a retry is attempted, but an abrupt process termination can leave points behind. This simplified plan accepts the path-presence tradeoff; stronger crash-complete semantics would require a separate publication state design.

#### Legacy single-request example — do not implement

The old single-request example below is retained only to identify the behavior being removed:

```python
def upsert_file_chunks(client, collection_name, points_data):
    qdrant_points = [build all 10 PointStructs...]
    client.upsert(collection_name=..., points=qdrant_points)  # ONE call, all 10 at once
```

With batched writes, a stop or crash can occur after any acknowledged batch. Earlier batches may exist in Qdrant while later ones do not. Known failures are cleaned by file path; an abrupt crash is intentionally handled by the simple presence-based skip rule on the next run.

#### What actually needs cleanup

| Scenario | Qdrant state for this file | Action |
|---|---|---|
| Stop before the first batch | No new points for a new path | Leave the path absent so a later run can retry |
| Stop after one or more batches | Partial points may exist | Delete by file path when the worker observes the stop; otherwise the next path lookup may skip it |
| Every batch acknowledged | Points are searchable under the file path | Count the file as indexed |
| Forced reindex | Old points may exist | Delete all points for the path before writing replacement batches |
| Batch request times out | Outcome may be unknown | Retry deterministic IDs or delete the file path before retrying |

> [!IMPORTANT]
> Stop checks happen between batches. A stop during an HTTP call allows that bounded call to finish or time out. A successful individual batch does not prove that the complete file was written, but the simplified skip policy intentionally uses path presence.

The previous all-at-once consumer pseudocode has been removed because it was unsafe for large files. Implement the bounded loop in section 5d; do not accumulate `chunks`, `vectors`, or `points` for an entire document.

#### Required guarantee table

| When stop fires | Qdrant state | Action | Next run |
|---|---|---|---|
| During conversion/chunking/embedding | No new points for a new path | Retry later | Path remains absent |
| During batched upsert | Partial points may exist | Delete by path if observed; otherwise presence-based skip applies | Depends on whether cleanup ran |
| All batches complete | Full point set for the path | Count as indexed | Skipped by path on later runs |
| Forced reindex | Old point set may exist | Delete path first, then write bounded batches | Skipped by path after success |

### 9d. Stop event check placement in consumer

Check before conversion and between chunk/embedding batches. Do not interrupt an active Qdrant request; allow its bounded request to return or time out, then delete by file path if the worker can complete cleanup. A `RunStopped` condition is not a failed file.

```python
while True:
    item = file_queue.get()
    try:
        if item is None:                 # SENTINEL
            break
        if self.stop_event.is_set():     # CHECK 1: after dequeue
            continue                     # discard without processing

        # ... convert within configured time/resource budgets ...
        for chunk_batch in chunker.iter_chunk_batches(...):
            if self.stop_event.is_set():
                delete_points_by_file_path(...)
                break
            # embed and upsert one bounded batch; wait or time out

        # Count indexed only if every chunk batch completed and stop is not set.
    finally:
        file_queue.task_done()            # exactly once for every get()
```

> [!IMPORTANT]
> The upsert helper must be idempotent and bounded. Do not assume it is always fast; configure a network timeout and recover ambiguous outcomes.

### 9e. Producer stop — coordinator-owned shutdown

The producer does not enqueue sentinels. It exits on stop, queue failure, or traversal completion and records whether discovery completed. The coordinator then sends one sentinel to each live worker using timed puts. Workers use queue timeouts or sentinels to exit. Every dequeued item calls `task_done()` exactly once, including sentinels and stop-discarded items. Catch worker failures at the outer loop so one exception cannot silently remove a consumer and leave the producer blocked forever.

### 9f. Orchestrator join order

```python
# Producer queue puts use timeouts and fail/stop checks; consumers keep draining.
producer_thread.join(timeout=producer_shutdown_timeout)
if producer_thread.is_alive():
    request_run_failure("producer did not stop")

# Sentinels are ordered after producer exit, so no later work can follow them.
signal_consumers_with_sentinels(file_queue, live_workers, stop_event,
                                put_timeout=queue_put_timeout)
for worker in consumer_threads:
    worker.join(timeout=worker_shutdown_timeout)

if producer_thread.is_alive() or any(w.is_alive() for w in consumer_threads):
    # Keep run nonterminal and retain the cross-process run lease. Reconcile on startup.
    persist_stopping_state_and_owner()
else:
    reconcile_run_counters()
    persist_terminal_status()
```

> [!WARNING]
> `queue.join()` is not a substitute for thread lifecycle management and can block forever if any dequeued path misses `task_done()`. Use exactly-once `task_done()` in `finally`, but still join producer/workers with finite timeouts, detect stuck threads, and do not release the run lease or mark a terminal state while a thread can still write. A thread join can also time out; it is not inherently deadlock-proof.

---

## 10. Incremental XML Handling

Parse both XML inputs once, accept only `FILE` entries, normalize and de-duplicate canonical paths, and log malformed/ignored entries. Deleted paths remove all Qdrant points for the path and create a per-run tombstone so a file still on disk is not rediscovered in that run. Changed paths bypass the Qdrant existence check and are explicitly queued if they exist inside configured roots and pass exclusion/file-type rules. If a path is in both inputs, deletion takes precedence. Preserve XML input paths and parsed counts on `IndexRun` for audit. XML deletion must remove every matching point through paginated deletion, not only the first page.

---

## 11. Backward Compatibility Notes

| Concern | Resolution |
|---|---|
| Existing `index_run_files` rows in DB | Preserve and serve during the first release; no automatic drop |
| `GET /api/index/runs/{id}/files` | Preserve paginated behavior during compatibility window |
| `total_files` field in API/UI | Retain for historical runs; add discovery/processed/complete fields compatibly |
| `IndexRunFile` imports in routers | Keep until the endpoint is replaced through a separate migration |
| Tests mocking `IndexRunFile` | Keep history compatibility tests; add retention tests |

---

## 12. Tests to Update/Add

### Remove/rewrite
- `tests/test_routers/test_incremental.py` — remove any assertions on `IndexRunFile` rows
- `tests/test_indexer/` — update traverser tests (new signature, no Qdrant param)
- `tests/conftest.py` — remove `IndexRunFile` fixture setup if present

### New tests

#### `tests/test_indexer/test_runner_pipeline.py`
```python
def test_producer_pushes_items_to_queue():
    """Producer puts FileItems for enabled extensions; skips excluded paths."""

def test_producer_increments_discovered_on_each_valid_file():
    """Each non-skipped file increments discovered_files on IndexRun."""

def test_consumer_skips_when_qdrant_has_matching_file_path():
    """A non-forced file with a matching Qdrant path is skipped."""

def test_consumer_indexes_new_file_end_to_end():
    """New file -> bounded chunk/embed/upsert batches -> indexed_files."""

def test_embedding_and_upsert_batches_never_exceed_configured_limits():
    """Assert max chunk count, point count, and serialized request bytes."""

def test_partial_upsert_failure_removes_known_partial_points():
    """Observed partial writes are deleted so a later path check can retry."""

def test_changed_xml_deletes_existing_points_before_reindex():
    """Forced paths are deleted and indexed again without fingerprinting."""

def test_chunk_batches_do_not_retain_all_vectors_or_points():
    """Use a synthetic very large document and assert bounded batch sizes."""

def test_stop_event_halts_producer_before_full_walk():
    """Producer breaks out of walk when stop_event is set."""

def test_stop_event_drains_consumer_without_processing():
    """Consumer safely drains queued paths without starting new work."""

def test_worker_failure_does_not_deadlock_producer_or_shutdown():
    """Producer and remaining consumers terminate on worker failure/stop."""

def test_configured_worker_and_embed_concurrency_limits_are_respected():
    """Conversion and model inference limits are independent and bounded."""

def test_run_history_retention_does_not_drop_legacy_rows():
    """Migration is additive and preserves existing IndexRunFile rows."""

def test_deleted_xml_path_is_not_rediscovered_when_file_still_exists():
    """Deleted tombstone takes precedence over folder traversal for this run."""

def test_changed_xml_path_forces_reindex_and_deleted_wins_conflict():
    """Changed paths bypass unchanged checks; deleted wins if listed in both."""

def test_duplicate_and_case_variant_paths_are_canonicalized_once():
    """Each document path is processed once per run on Windows."""
```

#### `tests/test_indexer/test_traverser.py`
```python
def test_walk_folders_stream_skips_excluded_path():
def test_walk_folders_stream_skips_disabled_extension():
def test_walk_folders_stream_yields_pending_for_valid_file():
def test_walk_folders_stream_no_qdrant_calls():
    """walk_folders_stream must not call any Qdrant functions."""

def test_walk_folders_stream_honors_changed_and_deleted_path_sets():
    """Force changed files and suppress deleted paths still present on disk."""

def test_walk_folders_stream_stops_on_stop_event():
    """Generator yields no more items after stop_event.set()."""
```

#### `tests/test_routers/test_index.py`
```python
def test_status_reports_discovery_complete_and_terminal_counts():
    """Status distinguishes live discovery from determinate completed progress."""

def test_run_files_endpoint_remains_paginated_during_compatibility_window():
    """Legacy run details continue to be available after additive migration."""

def test_runs_list_has_discovered_files_field():
    """GET /api/index/runs lists runs with discovered_files field."""
```

---

## 13. Implementation Order

Execute in this order to keep the app functional throughout:

| Order | File | Action |
|---|---|---|
| 1 | `app/indexer/qdrant_ops.py`, `app/indexer/embedder.py` | Implement and unit-test the bounded `file_path` lookup, strict embedding/point-count/byte batches, and deterministic IDs |
| 2 | `app/indexer/chunker/`, `app/indexer/converter.py` | Add chunk iterators, per-chunk limits, expanded-text limits, and document memory controls |
| 3 | `app/models.py`, `app/database.py`, `app/main.py` | Add run counters and additive versioned migration; preserve old run tables and verify backup/upgrade |
| 4 | `app/indexer/traverser.py`, `app/indexer/runner.py` | Add bounded queues/worker lifecycle, XML force/tombstone rules, batched counters, startup recovery |
| 5 | `app/search/engine.py`, `app/routers/reclassify.py` | Preserve bounded search and paginate all-point reclassification |
| 6 | `app/routers/index.py`, templates, JS | Expose accurate discovery/processed/status counters while retaining API compatibility |
| 7 | `tests/` | Add fault, migration, batch-bound, large-file, stop/restart, and XML regression coverage |
| 8 | Benchmark/smoke test | Run synthetic large corpus and representative large documents; measure RSS, queue depth, throughput, and recovery |

> [!IMPORTANT]
> Each phase must keep the current application bootable. Use additive migration and a verified backup. Do not deploy schema/model changes that delete `IndexRunFile` history in the same change as the pipeline unless a separately reviewed export/retention migration exists.

---

## 14. UI Changes Required

### 14a. `app/templates/dashboard.html` — changes needed

#### Change 1: Replace `total-count` with `discovered-count`

Current line 27:
```html
<span id="indexed-count">0</span> / <span id="total-count">0</span> files processed
```

New:
```html
<span id="processed-count">0</span> / <span id="discovered-count">~</span> discovered
(<span id="indexed-count">0</span> indexed)
<span class="progress-hint" id="progress-hint"></span>
```

> [!NOTE]
> The `~` initial value signals to users that discovery is in progress. The label "discovered" is more accurate than "total" since the total is not known upfront.

#### Change 2: Add a "Discovering..." animation indicator

Add below the progress bar:
```html
<div id="discovery-indicator" class="discovery-pulse" style="display:none;">
    <span class="pulse-dot"></span> Discovering files...
</div>
```

Show this element while `status === 'RUNNING' && !discovery_complete`; hide it after discovery ends, even if processing continues.

#### Change 3: Update "Recent Index Runs" table header

Current `<th>Total</th>` (line 88 in `dashboard.html`) maps to `total_files`.

Change to:
```html
<th>Discovered</th>
```

---

### 14b. `static/js/app.js` — changes needed

#### Change 1: `updateDashboardStatus()` — fix field name (line 68)

Current code:
```javascript
document.getElementById('total-count').innerText = data.total_files || 0;
```

New code:
```javascript
document.getElementById('discovered-count').innerText =
    data.discovery_complete ? data.discovered_files : `${data.discovered_files}…`;
document.getElementById('processed-count').innerText = data.processed_files || 0;
document.getElementById('indexed-count').innerText = data.indexed_files || 0;
document.getElementById('progress-hint').innerText =
    data.discovery_complete ? '' : 'Discovering files';
if (data.progress_percentage == null) {
    showIndeterminateProgress();
} else {
    showDeterminateProgress(data.progress_percentage);
}
```

#### Change 2: `updateDashboardStatus()` — add STOPPING visual state

Current stop-button logic (lines 75–81) just disables the button during STOPPING. Extend:

```javascript
const discoveryIndicator = document.getElementById('discovery-indicator');
const hint = document.getElementById('progress-hint');
const isDiscovering = data.status === 'RUNNING' && !data.discovery_complete;
if (discoveryIndicator) discoveryIndicator.style.display = isDiscovering ? 'flex' : 'none';

if (data.status === 'RUNNING') {
    if (btnStart) btnStart.disabled = true;
    if (btnStop) btnStop.disabled = false;
    if (hint) hint.innerText = isDiscovering ? 'Discovering files' : '';
} else if (data.status === 'STOPPING') {
    if (btnStart) btnStart.disabled = true;
    if (btnStop) btnStop.disabled = true;  // can't stop twice
    if (discoveryIndicator) discoveryIndicator.style.display = 'none';
    if (hint) hint.innerText = 'Stopping — finishing in-progress files...';
} else {
    if (btnStart) btnStart.disabled = false;
    if (btnStop) btnStop.disabled = true;
    if (discoveryIndicator) discoveryIndicator.style.display = 'none';
    if (hint) hint.innerText = '';
    // Reload runs table when run finishes
    if (data.status === 'COMPLETED' || data.status === 'STOPPED') {
        loadRecentRuns();
    }
}
```

> [!TIP]
> Adding `loadRecentRuns()` on completion/stop means the table auto-refreshes when a run finishes, without the user needing to reload the page.

#### Change 3: `loadRecentRuns()` — fix `total_files` → `discovered_files` (line 124)

Current:
```javascript
<td>${run.total_files}</td>
```

New:
```javascript
<td>${run.discovered_files ?? run.total_files ?? 0}</td>
```

> [!NOTE]
> The `?? run.total_files` fallback handles old run records in the DB that still have `total_files` but no `discovered_files`.

#### Change 4: Add `stat-discovered` card to the stats grid in `dashboard.html`

Optional but recommended — add a 5th stat card for live discovery count:

```html
<div class="card stat-box stat-discovered">
    <div class="stat-icon"><svg class="ui-icon" aria-hidden="true"><use href="#icon-search"></use></svg></div>
    <div class="stat-content">
        <span class="stat-number" id="stat-discovered">0</span>
        <span class="stat-label">Files Found</span>
    </div>
</div>
```

And in `updateDashboardStatus()` JS:
```javascript
const statDiscovered = document.getElementById('stat-discovered');
if (statDiscovered) statDiscovered.innerText = data.discovered_files || 0;
```

---

### 14c. Summary of UI changes

| Location | Element / Function | Change |
|---|---|---|
| `dashboard.html` line 27 | `<span id="total-count">` | Rename to `id="discovered-count"`, label to "discovered" |
| `dashboard.html` line 88 | `<th>Total</th>` (runs table) | Change to `<th>Discovered</th>` |
| `dashboard.html` stats grid | New stat card | Add "Files Found" card (optional but good) |
| `dashboard.html` progress section | New element | Add discovery-in-progress and indeterminate progress display |
| `app.js` status rendering | New state fields | Read discovery completion, discovered and processed counters |
| `app.js` line 75–81 | STOPPING state | Add hint text; disable Stop button; hide discovery indicator |
| `app.js` line 77 | Stop button disabled during STOPPING | Already correct — keep |
| `app.js` run table | Historical compatibility | Prefer new discovery count; fall back to legacy `total_files` |
| `app.js` RUNNING→COMPLETED transition | Run history reload | Add `loadRecentRuns()` call when status becomes COMPLETED or STOPPED |

> [!IMPORTANT]
> No new endpoints are required. Extend the existing status and runs responses while retaining `total_files` for historical clients. Show an indeterminate indicator until discovery completes; after that, progress is `processed / discovered`.

---

## Summary of Changes

| What | Before | After |
|---|---|---|
| Discovery phase | Collect ALL files into list first, then index | Producer streams files into bounded queue immediately |
| Per-run file rows | A row for every file, including every unchanged/skipped path | Keep bounded recent outcome details; preserve legacy history |
| Skip check | One serialized Qdrant scroll per traversed path | Worker performs one bounded Qdrant `file_path` lookup per non-forced candidate |
| Progress denominator | Known only after full discovery | Live discovered/processed counters; determinate percentage after discovery completes |
| Resume after stop | Replay pending rows from the last stopped run | Rewalk; skip paths found in Qdrant; changed XML forces reindex |
| Memory for large corpus | All candidate paths, futures, chunks, vectors, points retained | Bounded queues, bounded chunks/embeddings/point requests, explicit document budgets |
| Parallelism scope | One setting reused for file/embedding work | Separate file workers, model inference concurrency, batch size, queue capacity |

---

## 15. Additional Large-Corpus Code Audit

This audit is based on the current implementation in `app/`; the items below should be addressed as part of this refactor or explicitly deferred with measured evidence.

| Priority | Code | Finding | Required action |
|---|---|---|---|
| P0 | `app/indexer/runner.py::_execute_run` | Builds `files_to_process` for the full corpus, then submits one future per path. | Replace with lazy traversal and a bounded queue/worker pool; never submit all work up front. |
| P0 | `app/indexer/runner.py::_process_single_file` | Retains full markdown, all chunks, `chunk_texts`, all vectors, and all points per file. Several lists duplicate references/data. | Stream chunk batches through embedding and point batches; set per-file expanded-text and max-chunk budgets. |
| P0 | `app/indexer/embedder.py::embed_batch` | `encode(batch_size=32)` still returns all vectors for all input texts. | Bound the caller's input and output to `embedding_batch_size`; serialize/limit concurrent model calls and tune `torch`/BLAS threads. |
| P0 | `app/indexer/qdrant_ops.py::upsert_file_chunks` | Converts all points to a second list and makes one request with no count/byte cap. | Replace with a bounded batch API; enforce count and encoded-byte limits, deterministic IDs, `wait=True`, finite network timeout, and safe retry. |
| P0 | `app/indexer/chunker/*.py`, `chunker/base.py` | Every chunker returns a full `List[ChunkResult]`; heading, slide, and Excel implementations create additional whole-document intermediate lists. | Add lazy `iter_chunks`/`iter_chunk_batches` per format. Make `chunk_total` optional or remove it because a stream may not know the total in advance. Bound individual chunk characters/tokens, table rows, and parser expansion. |
| P0 | `app/indexer/converter.py::convert` | MarkItDown returns a complete `text_content` string. A 100 MB source limit does not limit expanded markdown/RAM. | Keep a hard expanded-text budget now; add format-specific disk spooling/streaming where supported. Treat one-file conversion memory as an explicit, measured floor until streaming extraction exists. |
| P0 | `app/indexer/qdrant_ops.py::check_file_exists_and_unchanged` | The existing check performs an unnecessary mtime comparison and is called during discovery. | Replace it with a bounded `file_path` existence lookup in workers; no hashing or manifest. Changed XML bypasses the lookup. |
| P0 | `app/indexer/runner.py` incremental phase | Deleted XML vectors are removed before traversal, so a still-present disk file can be reindexed. | Build normalized per-run changed/deleted sets; suppress deleted paths and force changed paths; deletion wins conflicts. |
| P1 | `app/indexer/traverser.py::walk_folders` | Performs a Qdrant scroll request per file, serially during directory walk; `os.walk()` also materializes each directory's child-name lists. | Remove Qdrant from traversal; perform the accepted per-file `file_path` lookup in workers. De-duplicate overlapping roots without a corpus-sized `seen_paths` set. Use `scandir`/disk-backed path de-dup if a single directory can be huge. |
| P1 | `app/indexer/runner.py` producer/counters | A database commit per discovered file would serialize SQLite writes. | Accumulate counters per producer/worker and flush deltas periodically or in small transactions; reconcile at finalization. |
| P1 | `app/indexer/runner.py` model/converter/Qdrant sharing | A shared embedder is cached safely at construction, but `model.encode()` concurrency is unbounded; shared MarkItDown converter thread safety is not established; one Qdrant client is passed to all workers. | Use separate converter instances per worker. Add a model inference semaphore/worker with configurable concurrency independent of conversion workers. Verify Qdrant client thread-safety for the selected transport; otherwise create one client per worker and close it deterministically. |
| P1 | `app/indexer/qdrant_ops.py::update_payload_for_file` | Scrolls only 500 points and updates only that first page. Large documents can remain partly reclassified. | Paginate until cursor exhaustion, apply payload updates in bounded batches, and return explicit success/failure and updated count. |
| P1 | `app/indexer/qdrant_ops.py::delete_points_by_file_path` | Returns `1` for any successful request and hides exceptions as `0`, even when a file has hundreds of chunks. | Return an operation outcome separately from a known document count. Track `deleted_files` by unique XML paths actually handled; expose delete errors. |
| P1 | `app/indexer/qdrant_ops.py::ensure_collection` | Payload indexes are created only when the collection itself is new. Existing collections may lack indexes after an upgrade. | Ensure the `file_path` payload index idempotently on existing collections too. |
| P1 | `app/indexer/runner.py::is_running` and API start | The active-run lock is in process memory. Multiple Uvicorn worker processes or a restart can allow concurrent runs or leave a run stuck as `running`. | Use a DB lease/owner token with expiry and startup reconciliation; claim a run transactionally. Keep the in-process flag only as a fast local guard. |
| P1 | `app/indexer/runner.py` daemon/background lifecycle | Daemon execution may be terminated during app shutdown after partial writes. | Use explicit shutdown coordination and finite converter/Qdrant timeouts; clean up partial points when failures are observed. |
| P0 | `app/search/engine.py::search` | Search is bounded by top-K; current pagination/`total_files` also count only top-K, not the entire collection. | Preserve the existing top-K bound and document its pagination semantics; do not raise search limits without a memory/latency budget. |
| P2 | `app/search/synonyms.py`, config routers | `.all()` loads synonyms and small admin configuration tables. These are currently bounded configuration data, not a corpus-sized scan. | No indexing refactor needed; add size limits to synonym/config input if these tables become user-scaled. |

### Current behaviors that are already bounded

- Do not add file hashing to the indexing path; the simplified skip decision uses the normalized Qdrant `file_path` only.
- Search asks Qdrant for a configured top-K and groups only those results, so its immediate result list is bounded. Preserve a hard maximum for `search_top_k` and excerpt count.
- Admin tables loaded with `.all()` are small configuration tables; prioritize the corpus-sized loops and Qdrant scrolls above.

---

## 16. Resource Limits and Defaults

Add independent settings, validate upper bounds, expose them in Settings, and log the effective values at run start. Keep `parallel_workers` as a compatibility alias for `index_workers` for at least one release.

| Setting | Bounds | Purpose |
|---|---|---|
| `index_workers` | Positive, capped | Concurrent documents being converted/chunked |
| `index_queue_capacity` | Positive, capped | Maximum queued path records; queue operations use timeouts |
| `embedding_batch_size` | Positive, capped | Maximum chunk texts and vectors retained for one encoder call |
| `embedding_concurrency` | 1 by default; explicitly capped | Concurrent calls into the shared model |
| `qdrant_upsert_batch_size` | Positive, capped | Maximum points per Qdrant write |
| `qdrant_upsert_max_bytes` | Positive, capped | Maximum request bytes, including payload text/vectors and a measured allowance for SDK serialization copies |
| `max_file_size_mb` | Existing setting, enforce before conversion | Source file guard |
| `max_markdown_chars` | New hard limit | Reject/truncate downstream work after conversion; does not by itself cap conversion peak memory |
| `max_chunk_chars` | New hard limit | Guard a single oversized chunk/table row |
| `conversion_timeout_seconds` | Finite | Prevent a converter from holding a worker forever |
| `qdrant_timeout_seconds` | Finite | Bound network wait and make ambiguous retries recoverable |
| `counter_flush_interval` | Count and/or time based | Limit SQLite write contention |

Do not guess production values from the sample folder. Start with conservative defaults for the actual host, then tune from RSS/throughput benchmarks. The total memory budget must account for model memory plus `index_workers × (conversion output + one chunk batch + one vector batch + one point batch)`, not just the queue capacity. Until conversion itself is bounded (streamed/spooled or run in an OS-limited subprocess), the conversion-output term remains a potentially unbounded peak; a post-conversion character check is not a hard RAM guarantee.

---

## 17. Rollout and Acceptance Criteria

### Rollout order

1. Add run counters and settings through an additive migration; create a verified backup and retain existing run/file history.
2. Add or verify the Qdrant `file_path` payload index; no legacy manifest backfill is required.
3. Implement the bounded worker-side path lookup, deterministic point IDs, and known-failure cleanup.
4. Implement format-level chunk iterators and a disk-spooled/streaming conversion path for supported formats. Until then, reject above a measured output budget and explicitly do not claim arbitrary-large-document support.
5. Implement bounded embedding calls and count/byte-bounded Qdrant point batches. Keep the old pipeline behind a feature flag until failure/restart tests pass.
6. Implement bounded discovery, changed/deleted XML precedence, and worker shutdown/recovery.
7. Deploy with conservative concurrency; observe RSS, batch sizes, Qdrant latency, SQLite lock errors, failures, and queue depth before raising limits.
8. Consider pruning old `IndexRunFile` rows only after export, a retention period, and confirmation that the existing API/UI no longer requires them.

### Required acceptance checks

- A synthetic corpus with at least 50,000 paths begins indexing before discovery finishes; no path/future/seen-path list grows with the whole corpus. Include a single flat directory with many entries and overlapping configured roots.
- A synthetic document with a very high chunk count never exceeds configured embedding count, point count, or request-byte limits; RSS remains bounded by configured workers and per-file budgets rather than total chunks.
- A converter producing huge expanded output is stopped/spooled within a measured disk/RAM budget; a single oversized chunk is rejected before it can create an oversized embedding or Qdrant request. Post-conversion checks alone do not pass this criterion.
- Injected timeout after any Qdrant batch is surfaced, known partial points are deleted, and the failed file is recorded rather than silently reported as successful.
- Repeating a batch with the same deterministic IDs does not create duplicate chunks; forced reindex deletes the old file points before replacement.
- Stop during discovery, conversion, embedding, and Qdrant upsert ends cleanly or within explicit timeout; observed partial points are cleaned by file path.
- Deleted XML paths are deleted and remain excluded for that run even if the file is still on disk. Changed XML paths are forced exactly once. Duplicate/case-variant paths normalize once; deleted wins conflicts.
- Reclassification updates every chunk for a file with more than 500 chunks and reports errors instead of silently returning a partial success.
- Migration preserves existing `index_runs`, `index_run_files`, settings, and Qdrant collection contents; a failed migration can be retried or rolled back from backup. No manifest backfill is performed.
- Benchmark records peak RSS, files/minute, chunks/second, Qdrant upsert latency, queue high-water mark, SQLite busy/locked errors, and recovery time for both many-small-file and few-very-large-file workloads.
