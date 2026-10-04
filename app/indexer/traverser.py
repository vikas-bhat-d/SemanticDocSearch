import fnmatch
import os
import threading
from typing import Any, Dict, Generator, Iterable, List, Optional, Set

from sqlalchemy.orm import Session

from app.indexer.paths import canonical_file_path, normalize_file_path, path_is_within
from app.models import ExcludedPath, FileTypeConfig, IndexFolder


def is_path_excluded(file_path: str, path_exclusions: List[str]) -> bool:
    norm_path = file_path.replace("/", "\\").lower()
    for exclusion in path_exclusions:
        norm_ex = exclusion.replace("/", "\\").lower()
        if norm_path.startswith(norm_ex) or fnmatch.fnmatch(norm_path, norm_ex):
            return True
    return False


def is_ext_excluded(ext: str, ext_exclusions: List[str]) -> bool:
    norm_ext = ext.lower()
    if not norm_ext.startswith("."):
        norm_ext = f".{norm_ext}"
    for exclusion in ext_exclusions:
        norm_ex = exclusion.lower()
        if not norm_ex.startswith("."):
            norm_ex = f".{norm_ex}"
        if norm_ext == norm_ex:
            return True
    return False


def _unique_roots(folder_paths: Iterable[str]) -> List[str]:
    """Remove duplicate and nested roots before walking them."""
    roots: List[str] = []
    for raw in sorted({normalize_file_path(p) for p in folder_paths if p}, key=len):
        if not any(path_is_within(raw, root) for root in roots):
            roots.append(raw)
    return roots


def _load_traversal_rules(db: Session):
    exclusions = db.query(ExcludedPath).all()
    path_exclusions = [e.value for e in exclusions if e.type == "path"]
    ext_exclusions = [e.value for e in exclusions if e.type == "extension"]
    enabled_exts = {
        row.extension.lower(): row.chunker
        for row in db.query(FileTypeConfig).filter_by(enabled=1).all()
    }
    return path_exclusions, ext_exclusions, enabled_exts


def _build_file_item(
    file_path: str,
    path_exclusions: List[str],
    ext_exclusions: List[str],
    enabled_exts: Dict[str, str],
    changed_paths: Set[str],
    require_exists: bool = False,
) -> Dict[str, Any]:
    file_path = normalize_file_path(file_path)
    canonical_path = canonical_file_path(file_path)
    file_name = os.path.basename(file_path)

    if require_exists and not os.path.isfile(file_path):
        return {
            "file_path": file_path,
            "canonical_path": canonical_path,
            "status": "skipped",
            "reason": "Changed file does not exist",
        }
    if is_path_excluded(file_path, path_exclusions):
        return {
            "file_path": file_path,
            "canonical_path": canonical_path,
            "status": "skipped",
            "reason": "Excluded path",
        }

    ext = os.path.splitext(file_name)[1].lower()
    if is_ext_excluded(ext, ext_exclusions):
        return {
            "file_path": file_path,
            "canonical_path": canonical_path,
            "status": "skipped",
            "reason": "Excluded extension",
        }
    if ext not in enabled_exts or not enabled_exts[ext]:
        return {
            "file_path": file_path,
            "canonical_path": canonical_path,
            "status": "skipped",
            "reason": "Unsupported or disabled extension",
        }

    return {
        "file_path": file_path,
        "canonical_path": canonical_path,
        "file_name": file_name,
        "extension": ext,
        "force_reindex": canonical_path in changed_paths,
        "status": "pending",
    }


def iter_incremental_file_items(
    db: Session,
    changed_paths: Dict[str, str],
    deleted_paths: Optional[Set[str]] = None,
    stop_event: Optional[threading.Event] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Yield changed XML files directly, without walking their parent folders."""
    stop_event = stop_event or threading.Event()
    deleted = {canonical_file_path(p) for p in (deleted_paths or set())}
    normalized_paths = {
        canonical_file_path(path): normalize_file_path(path)
        for path in changed_paths.values()
    }
    changed_keys = set(normalized_paths) - deleted
    path_exclusions, ext_exclusions, enabled_exts = _load_traversal_rules(db)
    db.rollback()

    for canonical_path in sorted(changed_keys):
        if stop_event.is_set():
            return
        file_path = normalized_paths[canonical_path]
        yield _build_file_item(
            file_path,
            path_exclusions,
            ext_exclusions,
            enabled_exts,
            changed_keys,
            require_exists=True,
        )


def walk_folders_stream(
    db: Session,
    stop_event: Optional[threading.Event] = None,
    changed_paths: Optional[Set[str]] = None,
    deleted_paths: Optional[Set[str]] = None,
    folder_paths: Optional[Iterable[str]] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Yield filesystem candidates lazily without making Qdrant requests."""
    stop_event = stop_event or threading.Event()
    changed = {canonical_file_path(p) for p in (changed_paths or set())}
    deleted = {canonical_file_path(p) for p in (deleted_paths or set())}

    if folder_paths is None:
        folder_paths = (
            row.path
            for row in db.query(IndexFolder)
            .filter(IndexFolder.status.in_(("pending", "failed", "stopped")))
            .all()
        )
    folders = _unique_roots(folder_paths)
    path_exclusions, ext_exclusions, enabled_exts = _load_traversal_rules(db)
    # The generator may walk a large tree for a long time.  End the read
    # transaction before yielding files so progress writes are not blocked.
    db.rollback()

    for folder_path in folders:
        if stop_event.is_set():
            return
        if not os.path.exists(folder_path) or is_path_excluded(folder_path, path_exclusions):
            continue

        for root, dirs, files in os.walk(folder_path):
            if stop_event.is_set():
                return
            dirs[:] = [
                directory for directory in dirs
                if not is_path_excluded(os.path.join(root, directory), path_exclusions)
            ]

            for file_name in files:
                if stop_event.is_set():
                    return

                file_path = normalize_file_path(os.path.join(root, file_name))
                canonical_path = canonical_file_path(file_path)
                if canonical_path in deleted:
                    continue

                yield _build_file_item(
                    file_path,
                    path_exclusions,
                    ext_exclusions,
                    enabled_exts,
                    changed,
                )


def walk_folders(
    db: Session,
    qdrant_client: Any = None,
    collection_name: Optional[str] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Compatibility wrapper; Qdrant arguments are intentionally ignored."""
    yield from walk_folders_stream(db)
