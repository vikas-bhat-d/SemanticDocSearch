import os
import fnmatch
from datetime import datetime
from typing import Generator, List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import IndexFolder, ExcludedPath, FileTypeConfig
from app.indexer.qdrant_ops import check_file_exists_and_unchanged
from qdrant_client import QdrantClient


def is_path_excluded(file_path: str, path_exclusions: List[str]) -> bool:
    norm_path = file_path.replace('/', '\\').lower()
    for ex in path_exclusions:
        norm_ex = ex.replace('/', '\\').lower()
        if norm_path.startswith(norm_ex) or fnmatch.fnmatch(norm_path, norm_ex):
            return True
    return False


def is_ext_excluded(ext: str, ext_exclusions: List[str]) -> bool:
    norm_ext = ext.lower()
    if not norm_ext.startswith("."):
        norm_ext = f".{norm_ext}"
    for ex in ext_exclusions:
        norm_ex = ex.lower()
        if not norm_ex.startswith("."):
            norm_ex = f".{norm_ex}"
        if norm_ext == norm_ex:
            return True
    return False


def walk_folders(
    db: Session,
    qdrant_client: Optional[QdrantClient] = None,
    collection_name: Optional[str] = None
) -> Generator[Dict[str, Any], None, None]:
    folders = [f.path for f in db.query(IndexFolder).all()]
    exclusions = db.query(ExcludedPath).all()

    path_exclusions = [e.value for e in exclusions if e.type == 'path']
    ext_exclusions = [e.value for e in exclusions if e.type == 'extension']

    enabled_exts = {
        row.extension.lower(): row.chunker
        for row in db.query(FileTypeConfig).filter_by(enabled=1).all()
    }

    for folder_path in folders:
        if not os.path.exists(folder_path):
            continue

        if is_path_excluded(folder_path, path_exclusions):
            continue

        for root, dirs, files in os.walk(folder_path):
            # Prune excluded subdirectories
            dirs[:] = [
                d for d in dirs
                if not is_path_excluded(os.path.join(root, d), path_exclusions)
            ]

            for file_name in files:
                file_path = os.path.join(root, file_name)
                ext = os.path.splitext(file_name)[1].lower()

                if is_path_excluded(file_path, path_exclusions):
                    yield {"file_path": file_path, "status": "skipped", "reason": "Excluded path"}
                    continue

                if is_ext_excluded(ext, ext_exclusions):
                    yield {"file_path": file_path, "status": "skipped", "reason": "Excluded extension"}
                    continue

                if ext not in enabled_exts:
                    yield {"file_path": file_path, "status": "skipped", "reason": "Unsupported or disabled extension"}
                    continue

                try:
                    mtime = os.path.getmtime(file_path)
                    modified_at_iso = datetime.utcfromtimestamp(mtime).isoformat()
                except Exception as e:
                    yield {"file_path": file_path, "status": "failed", "reason": f"Cannot read mtime: {str(e)}"}
                    continue

                # Check Qdrant skip logic
                if qdrant_client and collection_name:
                    if check_file_exists_and_unchanged(qdrant_client, collection_name, file_path, modified_at_iso):
                        yield {"file_path": file_path, "status": "skipped", "reason": "Unchanged file already in Qdrant"}
                        continue

                yield {
                    "file_path": file_path,
                    "file_name": file_name,
                    "extension": ext,
                    "modified_at_iso": modified_at_iso,
                    "status": "pending"
                }
