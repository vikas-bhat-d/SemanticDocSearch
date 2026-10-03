import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import require_session_api
from app.models import IncrementalXmlConfig
from app.indexer.xml_parser import parse_incremental_xml

router = APIRouter(prefix="/api/incremental", tags=["incremental"])


class XmlConfigSaveRequest(BaseModel):
    changed_xml_path: Optional[str] = None
    deleted_xml_path: Optional[str] = None


class PreviewRequest(BaseModel):
    changed_xml_path: Optional[str] = None
    deleted_xml_path: Optional[str] = None


@router.get("/config")
async def get_incremental_config(
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    cfg = db.query(IncrementalXmlConfig).filter_by(id=1).first()
    if not cfg:
        return {"changed_xml_path": "", "deleted_xml_path": ""}
    return {
        "changed_xml_path": cfg.changed_xml_path or "",
        "deleted_xml_path": cfg.deleted_xml_path or "",
        "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None
    }


@router.post("/config")
async def save_incremental_config(
    body: XmlConfigSaveRequest,
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    cfg = db.query(IncrementalXmlConfig).filter_by(id=1).first()
    if not cfg:
        cfg = IncrementalXmlConfig(id=1)
        db.add(cfg)

    cfg.changed_xml_path = body.changed_xml_path
    cfg.deleted_xml_path = body.deleted_xml_path
    db.commit()

    return {"status": "success", "message": "Incremental XML paths saved"}


@router.post("/preview")
async def preview_incremental_xml(
    body: PreviewRequest,
    auth: bool = Depends(require_session_api)
):
    affected = []

    for label, xml_path in [("changed", body.changed_xml_path), ("deleted", body.deleted_xml_path)]:
        if xml_path and xml_path.strip():
            if not os.path.exists(xml_path.strip()):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"XML file not found: {xml_path}"
                )
            parsed = parse_incremental_xml(xml_path.strip())
            for type_str, conv_path in parsed:
                affected.append({
                    "source": label,
                    "type": type_str,
                    "converted_path": conv_path
                })

    return {
        "total_affected": len(affected),
        "items": affected
    }
