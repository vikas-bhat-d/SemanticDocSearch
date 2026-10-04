from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import require_session_api
from app.config import get_config
from app.indexer.qdrant_ops import get_qdrant_client, update_payload_for_file

router = APIRouter(prefix="/api/reclassify", tags=["reclassify"])


class ReclassifyRequest(BaseModel):
    file_path: str
    departments: List[str]
    doc_types: List[str]


@router.post("")
async def reclassify_file(
    body: ReclassifyRequest,
    auth: bool = Depends(require_session_api),
    db: Session = Depends(get_db)
):
    if not body.file_path or not body.file_path.strip():
        raise HTTPException(status_code=400, detail="file_path cannot be empty")

    config = get_config(db)
    qdrant = get_qdrant_client(host=config.qdrant_host, port=config.qdrant_port)

    try:
        count = update_payload_for_file(
            client=qdrant,
            collection_name=config.collection_name,
            file_path=body.file_path,
            departments=body.departments,
            doc_types=body.doc_types,
            raise_errors=True,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Qdrant reclassification failed: {exc}",
        )

    return {
        "status": "success",
        "file_path": body.file_path,
        "updated_points": count
    }
