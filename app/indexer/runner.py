import os
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import IndexRun, IndexRunFile, IncrementalXmlConfig
from app.config import get_config
from app.logger import get_logger
from app.indexer.converter import DocumentConverter
from app.indexer.embedder import Embedder
from app.indexer.chunker.registry import get_chunker
from app.indexer.classifier import classify_file
from app.indexer.xml_parser import parse_incremental_xml
from app.indexer.traverser import walk_folders
from app.indexer.qdrant_ops import (
    get_qdrant_client,
    ensure_collection,
    delete_points_by_file_path,
    delete_points_by_folder_prefix,
    upsert_file_chunks
)


class IndexerRunner:
    def __init__(self):
        self.stop_event = threading.Event()
        self.is_running = False
        self.is_stopping = False
        self.current_run_id: Optional[int] = None
        self._thread: Optional[threading.Thread] = None

    def get_status(self, db: Session) -> Dict[str, Any]:
        if not self.current_run_id:
            last_run = db.query(IndexRun).order_by(IndexRun.id.desc()).first()
            if not last_run:
                return {
                    "status": "IDLE",
                    "run_id": None,
                    "total_files": 0,
                    "indexed_files": 0,
                    "skipped_files": 0,
                    "failed_files": 0,
                    "deleted_files": 0,
                    "progress_percentage": 0.0
                }
            run_status = last_run.status.upper()
            total = last_run.total_files or 0
            indexed = last_run.indexed_files or 0
            prog = (indexed / total * 100.0) if total > 0 else 0.0
            return {
                "status": run_status,
                "run_id": last_run.id,
                "total_files": total,
                "indexed_files": indexed,
                "skipped_files": last_run.skipped_files or 0,
                "failed_files": last_run.failed_files or 0,
                "deleted_files": last_run.deleted_files or 0,
                "progress_percentage": round(prog, 1),
                "started_at": last_run.started_at.isoformat() if last_run.started_at else None,
                "stopped_at": last_run.stopped_at.isoformat() if last_run.stopped_at else None
            }

        run = db.query(IndexRun).get(self.current_run_id)
        if not run:
            return {"status": "IDLE", "run_id": None}

        total = run.total_files or 0
        indexed = run.indexed_files or 0
        prog = (indexed / total * 100.0) if total > 0 else 0.0
        status_str = "STOPPING" if self.is_stopping else run.status.upper()

        return {
            "status": status_str,
            "run_id": run.id,
            "total_files": total,
            "indexed_files": indexed,
            "skipped_files": run.skipped_files or 0,
            "failed_files": run.failed_files or 0,
            "deleted_files": run.deleted_files or 0,
            "progress_percentage": round(prog, 1),
            "started_at": run.started_at.isoformat() if run.started_at else None
        }

    def start_run(
        self,
        changed_xml_path: Optional[str] = None,
        deleted_xml_path: Optional[str] = None
    ) -> int:
        if self.is_running or self.is_stopping:
            raise RuntimeError("An indexing run is already in progress")

        self.stop_event.clear()
        self.is_running = True
        self.is_stopping = False

        db = SessionLocal()
        try:
            config = get_config(db)

            # Persist XML paths if provided
            xml_cfg = db.query(IncrementalXmlConfig).filter_by(id=1).first()
            if not xml_cfg:
                xml_cfg = IncrementalXmlConfig(id=1)
                db.add(xml_cfg)

            if changed_xml_path is not None:
                xml_cfg.changed_xml_path = changed_xml_path
            if deleted_xml_path is not None:
                xml_cfg.deleted_xml_path = deleted_xml_path
            db.commit()

            c_xml = xml_cfg.changed_xml_path
            d_xml = xml_cfg.deleted_xml_path

            # Create new run record
            run = IndexRun(
                status="running",
                changed_xml_path=c_xml,
                deleted_xml_path=d_xml
            )
            db.add(run)
            db.commit()
            db.refresh(run)

            self.current_run_id = run.id

            # Start worker thread
            self._thread = threading.Thread(
                target=self._execute_run,
                args=(run.id, c_xml, d_xml),
                daemon=True
            )
            self._thread.start()
            return run.id
        finally:
            db.close()

    def stop_run(self):
        if not self.is_running:
            return
        self.is_stopping = True
        self.stop_event.set()

    def _execute_run(self, run_id: int, changed_xml: Optional[str], deleted_xml: Optional[str]):
        db = SessionLocal()
        log = get_logger(run_id=run_id)
        log.info("Starting index run %s", run_id)

        try:
            config = get_config(db)
            qdrant = get_qdrant_client(host=config.qdrant_host, port=config.qdrant_port)
            ensure_collection(qdrant, config.collection_name, config.embedding_dimensions)

            # 1. Incremental XML processing
            deleted_count = 0
            for xml_file in (changed_xml, deleted_xml):
                if xml_file and os.path.exists(xml_file):
                    entries = parse_incremental_xml(xml_file)
                    for type_str, path in entries:
                        if type_str == "FILE":
                            deleted_count += delete_points_by_file_path(qdrant, config.collection_name, path)
                        elif type_str == "FOLDER":
                            deleted_count += delete_points_by_folder_prefix(qdrant, config.collection_name, path)

            run = db.query(IndexRun).get(run_id)
            run.deleted_files = deleted_count
            db.commit()

            # 2. Collect pending files from previous stopped run
            pending_from_stopped = []
            last_stopped = db.query(IndexRun).filter_by(status="stopped").order_by(IndexRun.id.desc()).first()
            if last_stopped:
                prev_pending = db.query(IndexRunFile).filter_by(run_id=last_stopped.id, status="pending").all()
                for pf in prev_pending:
                    pending_from_stopped.append(pf.file_path)

            # 3. Collect files from folder traverser
            files_to_process = []
            seen_paths = set()

            for fp in pending_from_stopped:
                if os.path.exists(fp) and fp not in seen_paths:
                    seen_paths.add(fp)
                    rf = IndexRunFile(run_id=run_id, file_path=fp, status="pending")
                    db.add(rf)
                    files_to_process.append(fp)

            skipped_count = 0
            for item in walk_folders(db, qdrant_client=qdrant, collection_name=config.collection_name):
                fp = item["file_path"]
                if item["status"] == "skipped":
                    skipped_count += 1
                    rf = IndexRunFile(run_id=run_id, file_path=fp, status="skipped", error_message=item.get("reason"))
                    db.add(rf)
                elif item["status"] == "pending":
                    if fp not in seen_paths:
                        seen_paths.add(fp)
                        rf = IndexRunFile(run_id=run_id, file_path=fp, status="pending")
                        db.add(rf)
                        files_to_process.append(fp)

            run.total_files = len(files_to_process)
            run.skipped_files = skipped_count
            db.commit()

            log.info("Total candidate files: %d, Skipped: %d", len(files_to_process), skipped_count)

            # 4. Initialize shared pipeline instances
            converter = DocumentConverter(max_file_size_mb=config.max_file_size_mb)
            embedder = Embedder(model_name=config.embedding_model, dimensions=config.embedding_dimensions)

            # 5. Process files concurrently
            max_workers = max(1, config.parallel_workers)
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self._process_single_file,
                        run_id,
                        fp,
                        config,
                        converter,
                        embedder,
                        qdrant
                    ): fp
                    for fp in files_to_process
                }

                for future in as_completed(futures):
                    if self.stop_event.is_set():
                        log.info("Stop event detected in main loop")
                        break

            # Update final run status
            run = db.query(IndexRun).get(run_id)
            if self.stop_event.is_set():
                run.status = "stopped"
                log.info("Run %s stopped by user", run_id)
            else:
                run.status = "completed"
                log.info("Run %s completed successfully", run_id)

            run.stopped_at = datetime.utcnow()
            db.commit()

        except Exception as e:
            log.error("Run %s failed with error: %s", run_id, str(e), exc_info=True)
            run = db.query(IndexRun).get(run_id)
            if run:
                run.status = "failed"
                run.stopped_at = datetime.utcnow()
                db.commit()
        finally:
            self.is_running = False
            self.is_stopping = False
            db.close()

    def _process_single_file(
        self,
        run_id: int,
        file_path: str,
        config: Any,
        converter: DocumentConverter,
        embedder: Embedder,
        qdrant: Any
    ):
        if self.stop_event.is_set():
            return

        db = SessionLocal()
        log = get_logger(run_id=run_id, file_path=file_path)

        run_file = db.query(IndexRunFile).filter_by(run_id=run_id, file_path=file_path).first()
        if not run_file:
            db.close()
            return

        try:
            run_file.started_at = datetime.utcnow()
            run_file.status = "converting"
            db.commit()

            # 1. Convert to Markdown
            md_text = converter.convert(file_path)

            if self.stop_event.is_set():
                self._rollback_file(db, run_file, qdrant, config.collection_name)
                return

            # 2. Chunk text
            run_file.status = "chunking"
            db.commit()

            file_name = os.path.basename(file_path)
            ext = os.path.splitext(file_name)[1].lower()
            chunker = get_chunker(ext, db, config)

            if not chunker:
                run_file.status = "skipped"
                run_file.error_message = "No matching chunker configured"
                db.commit()
                db.query(IndexRun).filter_by(id=run_id).update({"skipped_files": IndexRun.skipped_files + 1})
                db.commit()
                return

            chunks = chunker.chunk(md_text, file_name)

            if not chunks:
                run_file.status = "skipped"
                run_file.error_message = "Chunker returned 0 chunks"
                db.commit()
                db.query(IndexRun).filter_by(id=run_id).update({"skipped_files": IndexRun.skipped_files + 1})
                db.commit()
                return

            if self.stop_event.is_set():
                self._rollback_file(db, run_file, qdrant, config.collection_name)
                return

            # 3. Embed chunks
            run_file.status = "embedding"
            db.commit()

            chunk_texts = [c.text for c in chunks]
            vectors = embedder.embed_batch(chunk_texts)

            if self.stop_event.is_set():
                self._rollback_file(db, run_file, qdrant, config.collection_name)
                return

            # 4. Upsert to Qdrant
            run_file.status = "indexing"
            db.commit()

            classification = classify_file(file_path, db)
            mtime = os.path.getmtime(file_path)
            modified_at_iso = datetime.utcfromtimestamp(mtime).isoformat()
            indexed_at_iso = datetime.utcnow().isoformat()

            # Compute SHA256 file hash
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk_data := f.read(65536):
                    hasher.update(chunk_data)
            file_hash = f"sha256:{hasher.hexdigest()}"

            points = []
            for c, vec in zip(chunks, vectors):
                points.append({
                    "vector": vec,
                    "payload": {
                        "file_path": file_path,
                        "file_name": file_name,
                        "file_extension": ext,
                        "departments": classification["departments"],
                        "doc_types": classification["doc_types"],
                        "chunk_index": c.chunk_index,
                        "chunk_total": c.chunk_total,
                        "section_context": c.section_context,
                        "content": c.text,
                        "file_modified_at": modified_at_iso,
                        "indexed_at": indexed_at_iso,
                        "file_hash": file_hash
                    }
                })

            upsert_file_chunks(qdrant, config.collection_name, points)

            if self.stop_event.is_set():
                self._rollback_file(db, run_file, qdrant, config.collection_name)
                return

            # Success
            run_file.status = "completed"
            run_file.chunks_indexed = len(chunks)
            run_file.completed_at = datetime.utcnow()
            db.commit()

            db.query(IndexRun).filter_by(id=run_id).update({"indexed_files": IndexRun.indexed_files + 1})
            db.commit()
            log.info("Successfully indexed %s (%d chunks)", file_name, len(chunks))

        except Exception as e:
            log.error("Failed processing file %s: %s", file_path, str(e))
            run_file.status = "failed"
            run_file.error_message = str(e)
            run_file.completed_at = datetime.utcnow()
            db.commit()

            db.query(IndexRun).filter_by(id=run_id).update({"failed_files": IndexRun.failed_files + 1})
            db.commit()
        finally:
            db.close()

    def _rollback_file(self, db: Session, run_file: IndexRunFile, qdrant: Any, collection_name: str):
        delete_points_by_file_path(qdrant, collection_name, run_file.file_path)
        run_file.status = "pending"
        db.commit()


# Singleton instance
indexer_runner = IndexerRunner()
