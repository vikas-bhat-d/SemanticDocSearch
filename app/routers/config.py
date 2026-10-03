import os
import json
import secrets
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.auth import require_session_api
from app.config import (
    get_config, reload_config, hash_secret, verify_secret,
    get_raw_initial_api_key
)
from app.logger import update_logger_level, log_queue
from app.models import (
    Config, IndexFolder, ExcludedPath, FileTypeConfig,
    Department, DocType, Synonym
)

router = APIRouter(prefix="/api", tags=["config"])


# Pydantic Request Models
class SettingsUpdateRequest(BaseModel):
    embedding_model: Optional[str] = None
    embedding_dimensions: Optional[int] = None
    parallel_workers: Optional[int] = None
    qdrant_host: Optional[str] = None
    qdrant_port: Optional[int] = None
    collection_name: Optional[str] = None
    log_level: Optional[str] = None
    chunk_size: Optional[int] = None
    chunk_overlap: Optional[int] = None
    rows_per_chunk: Optional[int] = None
    search_top_k: Optional[int] = None
    search_per_page: Optional[int] = None
    search_excerpt_count: Optional[int] = None
    max_file_size_mb: Optional[int] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None
    regenerate_api_key: Optional[bool] = False


class FolderCreateRequest(BaseModel):
    path: str


class ExclusionCreateRequest(BaseModel):
    value: str
    type: str  # 'path' | 'extension'


class FileTypeCreateRequest(BaseModel):
    extension: str
    chunker: str
    enabled: Optional[int] = 1


class FileTypeUpdateRequest(BaseModel):
    chunker: Optional[str] = None
    enabled: Optional[int] = None


class PatternGroupRequest(BaseModel):
    name: str
    path_patterns: List[str]


class SynonymRequest(BaseModel):
    term: str
    synonyms: List[str]


# --- SETTINGS ---
@router.get("/config/settings")
async def get_settings(
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    cfg = get_config(db)
    init_key = get_raw_initial_api_key()
    return {
        "embedding_model": cfg.embedding_model,
        "embedding_dimensions": cfg.embedding_dimensions,
        "parallel_workers": cfg.parallel_workers,
        "qdrant_host": cfg.qdrant_host,
        "qdrant_port": cfg.qdrant_port,
        "collection_name": cfg.collection_name,
        "log_level": cfg.log_level,
        "chunk_size": cfg.chunk_size,
        "chunk_overlap": cfg.chunk_overlap,
        "rows_per_chunk": cfg.rows_per_chunk,
        "search_top_k": cfg.search_top_k,
        "search_per_page": cfg.search_per_page,
        "search_excerpt_count": cfg.search_excerpt_count,
        "max_file_size_mb": cfg.max_file_size_mb,
        "initial_api_key": init_key
    }


@router.put("/config/settings")
async def update_settings(
    body: SettingsUpdateRequest,
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    current_cfg = get_config(db)
    new_api_key = None

    # Handle Password Change
    if body.new_password:
        if not body.old_password or not verify_secret(body.old_password, current_cfg.admin_password_hash):
            raise HTTPException(status_code=400, detail="Invalid current admin password")
        row = db.query(Config).filter_by(key="admin_password_hash").first()
        if row:
            row.value = hash_secret(body.new_password)

    # Handle API Key Regeneration
    if body.regenerate_api_key:
        new_api_key = f"sk-{secrets.token_hex(16)}"
        row = db.query(Config).filter_by(key="api_key_hash").first()
        if row:
            row.value = hash_secret(new_api_key)

    # Update generic config values
    update_dict = {
        "embedding_model": body.embedding_model,
        "embedding_dimensions": str(body.embedding_dimensions) if body.embedding_dimensions else None,
        "parallel_workers": str(body.parallel_workers) if body.parallel_workers else None,
        "qdrant_host": body.qdrant_host,
        "qdrant_port": str(body.qdrant_port) if body.qdrant_port else None,
        "collection_name": body.collection_name,
        "log_level": body.log_level,
        "chunk_size": str(body.chunk_size) if body.chunk_size else None,
        "chunk_overlap": str(body.chunk_overlap) if body.chunk_overlap else None,
        "rows_per_chunk": str(body.rows_per_chunk) if body.rows_per_chunk else None,
        "search_top_k": str(body.search_top_k) if body.search_top_k else None,
        "search_per_page": str(body.search_per_page) if body.search_per_page else None,
        "search_excerpt_count": str(body.search_excerpt_count) if body.search_excerpt_count else None,
        "max_file_size_mb": str(body.max_file_size_mb) if body.max_file_size_mb else None,
    }

    for k, v in update_dict.items():
        if v is not None:
            row = db.query(Config).filter_by(key=k).first()
            if not row:
                db.add(Config(key=k, value=str(v)))
            else:
                row.value = str(v)

    db.commit()
    reload_config(db)

    if body.log_level:
        update_logger_level(body.log_level)

    res = {"status": "success", "message": "Settings updated successfully"}
    if new_api_key:
        res["new_api_key"] = new_api_key
    return res


# --- FOLDERS ---
@router.get("/config/folders")
async def list_folders(auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    return db.query(IndexFolder).all()


@router.post("/config/folders")
async def add_folder(body: FolderCreateRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    p = body.path.strip()
    if not p:
        raise HTTPException(status_code=400, detail="Folder path cannot be empty")

    existing = db.query(IndexFolder).filter_by(path=p).first()
    if existing:
        raise HTTPException(status_code=409, detail="Folder path already added")

    folder = IndexFolder(path=p, status="pending")
    db.add(folder)
    db.commit()
    db.refresh(folder)
    return folder


@router.delete("/config/folders/{folder_id}")
async def delete_folder(folder_id: int, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    f = db.query(IndexFolder).get(folder_id)
    if not f:
        raise HTTPException(status_code=404, detail="Folder not found")
    db.delete(f)
    db.commit()
    return {"status": "success", "message": "Folder removed"}


# --- EXCLUSIONS ---
@router.get("/config/exclusions")
async def list_exclusions(auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    return db.query(ExcludedPath).all()


@router.post("/config/exclusions")
async def add_exclusion(body: ExclusionCreateRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    v = body.value.strip()
    t = body.type.strip().lower()
    if t not in ("path", "extension"):
        raise HTTPException(status_code=400, detail="Exclusion type must be 'path' or 'extension'")

    ex = ExcludedPath(value=v, type=t)
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex


@router.delete("/config/exclusions/{ex_id}")
async def delete_exclusion(ex_id: int, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    e = db.query(ExcludedPath).get(ex_id)
    if not e:
        raise HTTPException(status_code=404, detail="Exclusion not found")
    db.delete(e)
    db.commit()
    return {"status": "success", "message": "Exclusion removed"}


# --- FILE TYPES ---
@router.get("/config/file-types")
async def list_file_types(auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    return db.query(FileTypeConfig).all()


@router.post("/config/file-types")
async def add_file_type(body: FileTypeCreateRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    ext = body.extension.strip().lower()
    if not ext.startswith("."):
        ext = f".{ext}"

    if db.query(FileTypeConfig).filter_by(extension=ext).first():
        raise HTTPException(status_code=409, detail=f"Extension {ext} already configured")

    ft = FileTypeConfig(extension=ext, chunker=body.chunker.lower(), enabled=body.enabled)
    db.add(ft)
    db.commit()
    db.refresh(ft)
    return ft


@router.put("/config/file-types/{ft_id}")
async def update_file_type(ft_id: int, body: FileTypeUpdateRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    ft = db.query(FileTypeConfig).get(ft_id)
    if not ft:
        raise HTTPException(status_code=404, detail="File type config not found")

    if body.chunker is not None:
        ft.chunker = body.chunker.lower()
    if body.enabled is not None:
        ft.enabled = body.enabled

    db.commit()
    return ft


@router.delete("/config/file-types/{ft_id}")
async def delete_file_type(ft_id: int, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    ft = db.query(FileTypeConfig).get(ft_id)
    if not ft:
        raise HTTPException(status_code=404, detail="File type config not found")
    db.delete(ft)
    db.commit()
    return {"status": "success", "message": "File type removed"}


# --- DEPARTMENTS ---
@router.get("/config/departments")
async def list_departments(auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    deps = db.query(Department).all()
    res = []
    for d in deps:
        pats = json.loads(d.path_patterns) if isinstance(d.path_patterns, str) else d.path_patterns
        res.append({"id": d.id, "name": d.name, "path_patterns": pats})
    return res


@router.post("/config/departments")
async def add_department(body: PatternGroupRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    name = body.name.strip()
    if db.query(Department).filter_by(name=name).first():
        raise HTTPException(status_code=409, detail=f"Department '{name}' already exists")

    dept = Department(name=name, path_patterns=json.dumps(body.path_patterns))
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return {"id": dept.id, "name": dept.name, "path_patterns": body.path_patterns}


@router.put("/config/departments/{dept_id}")
async def update_department(dept_id: int, body: PatternGroupRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    dept = db.get(Department, dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Department name is required")
    if db.query(Department).filter(Department.name == name, Department.id != dept_id).first():
        raise HTTPException(status_code=409, detail=f"Department '{name}' already exists")

    dept.name = name
    dept.path_patterns = json.dumps(body.path_patterns)
    db.commit()
    return {"id": dept.id, "name": dept.name, "path_patterns": body.path_patterns}


@router.delete("/config/departments/{dept_id}")
async def delete_department(dept_id: int, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    d = db.query(Department).get(dept_id)
    if not d:
        raise HTTPException(status_code=404, detail="Department not found")
    db.delete(d)
    db.commit()
    return {"status": "success", "message": "Department removed"}


# --- DOC TYPES ---
@router.get("/config/doc-types")
async def list_doc_types(auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    dts = db.query(DocType).all()
    res = []
    for dt in dts:
        pats = json.loads(dt.path_patterns) if isinstance(dt.path_patterns, str) else dt.path_patterns
        res.append({"id": dt.id, "name": dt.name, "path_patterns": pats})
    return res


@router.post("/config/doc-types")
async def add_doc_type(body: PatternGroupRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    name = body.name.strip()
    if db.query(DocType).filter_by(name=name).first():
        raise HTTPException(status_code=409, detail=f"DocType '{name}' already exists")

    dt = DocType(name=name, path_patterns=json.dumps(body.path_patterns))
    db.add(dt)
    db.commit()
    db.refresh(dt)
    return {"id": dt.id, "name": dt.name, "path_patterns": body.path_patterns}


@router.put("/config/doc-types/{dt_id}")
async def update_doc_type(dt_id: int, body: PatternGroupRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    dt = db.get(DocType, dt_id)
    if not dt:
        raise HTTPException(status_code=404, detail="DocType not found")

    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Doc type name is required")
    if db.query(DocType).filter(DocType.name == name, DocType.id != dt_id).first():
        raise HTTPException(status_code=409, detail=f"DocType '{name}' already exists")

    dt.name = name
    dt.path_patterns = json.dumps(body.path_patterns)
    db.commit()
    return {"id": dt.id, "name": dt.name, "path_patterns": body.path_patterns}


@router.delete("/config/doc-types/{dt_id}")
async def delete_doc_type(dt_id: int, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    dt = db.query(DocType).get(dt_id)
    if not dt:
        raise HTTPException(status_code=404, detail="DocType not found")
    db.delete(dt)
    db.commit()
    return {"status": "success", "message": "DocType removed"}


# --- SYNONYMS ---
@router.get("/config/synonyms")
async def list_synonyms(auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    syns = db.query(Synonym).all()
    res = []
    for s in syns:
        syn_list = json.loads(s.synonyms) if isinstance(s.synonyms, str) else s.synonyms
        res.append({"id": s.id, "term": s.term, "synonyms": syn_list})
    return res


@router.post("/config/synonyms")
async def add_synonym(body: SynonymRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    term = body.term.strip().lower()
    if db.query(Synonym).filter_by(term=term).first():
        raise HTTPException(status_code=409, detail=f"Synonym term '{term}' already exists")

    syn = Synonym(term=term, synonyms=json.dumps(body.synonyms))
    db.add(syn)
    db.commit()
    db.refresh(syn)
    return {"id": syn.id, "term": syn.term, "synonyms": body.synonyms}


@router.put("/config/synonyms/{syn_id}")
async def update_synonym(syn_id: int, body: SynonymRequest, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    syn = db.query(Synonym).get(syn_id)
    if not syn:
        raise HTTPException(status_code=404, detail="Synonym not found")

    syn.term = body.term.strip().lower()
    syn.synonyms = json.dumps(body.synonyms)
    db.commit()
    return {"id": syn.id, "term": syn.term, "synonyms": body.synonyms}


@router.delete("/config/synonyms/{syn_id}")
async def delete_synonym(syn_id: int, auth: bool = Depends(require_session_api), db: Session = Depends(get_db)):
    syn = db.query(Synonym).get(syn_id)
    if not syn:
        raise HTTPException(status_code=404, detail="Synonym not found")
    db.delete(syn)
    db.commit()
    return {"status": "success", "message": "Synonym removed"}


# --- LOGS ---
@router.get("/logs/history")
async def get_log_history(
    lines: int = Query(500, ge=1, le=5000),
    level: Optional[str] = Query(None),
    auth: bool = Depends(require_session_api)
):
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "app.log")
    if not os.path.exists(log_file):
        return {"lines": []}

    results = []
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        all_lines = f.readlines()
        selected = all_lines[-lines:]
        for line in selected:
            if level and level.upper() not in line:
                continue
            results.append(line.strip())

    return {"lines": results}


@router.get("/logs/stream")
async def stream_logs(auth: bool = Depends(require_session_api)):
    async def event_generator():
        while True:
            try:
                log_item = log_queue.get_nowait()
                data = json.dumps(log_item)
                yield f"data: {data}\n\n"
            except Exception:
                await asyncio.sleep(0.5)
                yield ": keep-alive\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
