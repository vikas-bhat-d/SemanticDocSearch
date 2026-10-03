from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import require_auth, require_session_api, AuthContext
from app.models import IndexRun, IndexRunFile
from app.indexer.runner import indexer_runner

router = APIRouter(prefix="/api/index", tags=["index"])


class StartIndexRequest(BaseModel):
    changed_xml_path: Optional[str] = None
    deleted_xml_path: Optional[str] = None


@router.post("/start")
async def start_indexing(
    body: Optional[StartIndexRequest] = None,
    auth: AuthContext = Depends(require_auth),
    db: Session = Depends(get_db)
):
    changed_xml = body.changed_xml_path if body else None
    deleted_xml = body.deleted_xml_path if body else None

    try:
        run_id = indexer_runner.start_run(
            changed_xml_path=changed_xml,
            deleted_xml_path=deleted_xml
        )
        return {
            "status": "success",
            "message": "Indexing run started",
            "run_id": run_id
        }
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.post("/stop")
async def stop_indexing(
    auth: AuthContext = Depends(require_auth)
):
    if not indexer_runner.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No index run is currently active"
        )
    indexer_runner.stop_run()
    return {"status": "success", "message": "Stop signal issued to indexer"}


@router.get("/status")
async def get_index_status(
    auth: AuthContext = Depends(require_auth),
    db: Session = Depends(get_db)
):
    return indexer_runner.get_status(db)


@router.get("/runs")
async def list_index_runs(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    total = db.query(IndexRun).count()
    runs = (
        db.query(IndexRun)
        .order_by(IndexRun.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    items = [
        {
            "id": r.id,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "stopped_at": r.stopped_at.isoformat() if r.stopped_at else None,
            "status": r.status,
            "changed_xml_path": r.changed_xml_path,
            "deleted_xml_path": r.deleted_xml_path,
            "total_files": r.total_files,
            "indexed_files": r.indexed_files,
            "skipped_files": r.skipped_files,
            "failed_files": r.failed_files,
            "deleted_files": r.deleted_files
        }
        for r in runs
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }


@router.get("/runs/{run_id}/files")
async def list_run_files(
    run_id: int,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    query = db.query(IndexRunFile).filter(IndexRunFile.run_id == run_id)
    if status_filter:
        query = query.filter(IndexRunFile.status == status_filter.lower())

    total = query.count()
    files = (
        query.order_by(IndexRunFile.id.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    items = [
        {
            "id": f.id,
            "file_path": f.file_path,
            "status": f.status,
            "chunks_indexed": f.chunks_indexed,
            "error_message": f.error_message,
            "started_at": f.started_at.isoformat() if f.started_at else None,
            "completed_at": f.completed_at.isoformat() if f.completed_at else None
        }
        for f in files
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page
    }
