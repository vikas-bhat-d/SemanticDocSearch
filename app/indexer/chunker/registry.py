from typing import Optional
from sqlalchemy.orm import Session
from app.models import FileTypeConfig
from app.config import ConfigData, get_config
from app.indexer.chunker.base import BaseChunker
from app.indexer.chunker.excel import ExcelChunker
from app.indexer.chunker.heading import HeadingAwareChunker
from app.indexer.chunker.slide import SlideChunker
from app.indexer.chunker.generic import GenericChunker


CHUNKER_CLASSES = {
    "excel": ExcelChunker,
    "heading": HeadingAwareChunker,
    "slide": SlideChunker,
    "generic": GenericChunker,
}


def get_chunker(
    extension: str,
    db: Session,
    config: Optional[ConfigData] = None
) -> Optional[BaseChunker]:
    ext = extension.lower()
    if not ext.startswith("."):
        ext = f".{ext}"

    row = db.query(FileTypeConfig).filter_by(extension=ext, enabled=1).first()
    if not row:
        return None

    chunker_name = row.chunker.lower()
    cls = CHUNKER_CLASSES.get(chunker_name)
    if not cls:
        return None

    if config is None:
        config = get_config(db)

    if chunker_name == "excel":
        return cls(rows_per_chunk=config.rows_per_chunk)
    elif chunker_name == "heading":
        return cls(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    elif chunker_name == "slide":
        return cls(chunk_size=config.chunk_size)
    elif chunker_name == "generic":
        return cls(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)

    return cls()
