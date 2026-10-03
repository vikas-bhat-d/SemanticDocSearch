from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.search.engine import SearchEngine

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("")
async def search_documents(
    q: str = Query(..., description="Search query string"),
    department: Optional[List[str]] = Query(None, description="Filter by department"),
    doc_type: Optional[List[str]] = Query(None, description="Filter by doc type"),
    extension: Optional[List[str]] = Query(None, description="Filter by file extension"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    exact: bool = Query(False, description="Exact phrase search"),
    db: Session = Depends(get_db)
):
    if not q or not q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query parameter 'q' cannot be empty"
        )

    engine = SearchEngine(db)
    results = engine.search(
        query=q,
        departments=department,
        doc_types=doc_type,
        extensions=extension,
        page=page,
        per_page=per_page,
        exact=exact
    )
    return results
