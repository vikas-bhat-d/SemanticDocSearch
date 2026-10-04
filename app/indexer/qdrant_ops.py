import hashlib
import json
import math
import uuid
from typing import Any, Dict, Iterable, Iterator, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models

from app.indexer.paths import canonical_file_path, normalize_file_path


def _qdrant_timeout(timeout: Optional[float]) -> Optional[int]:
    """Convert application timeouts to the integer form required by Qdrant."""
    if timeout is None:
        return None
    return max(1, math.ceil(float(timeout)))


def get_qdrant_client(host: str = "localhost", port: int = 6333) -> QdrantClient:
    return QdrantClient(host=host, port=port)


def ensure_collection(client: QdrantClient, collection_name: str, dimensions: int = 384):
    collections = client.get_collections().collections
    exists = any(c.name == collection_name for c in collections)

    if not exists:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=rest_models.VectorParams(
                size=dimensions,
                distance=rest_models.Distance.COSINE,
            ),
        )

    # Also ensure indexes on an existing collection after upgrades.
    for field in ("file_path", "departments", "doc_types", "file_extension"):
        try:
            client.create_payload_index(
                collection_name=collection_name,
                field_name=field,
                field_schema=rest_models.PayloadSchemaType.KEYWORD,
            )
        except Exception:
            # Qdrant reports an error when an index already exists.  The
            # collection remains usable and this operation is idempotent.
            pass


def is_already_indexed(
    client: QdrantClient,
    collection_name: str,
    file_path: str,
    timeout: Optional[float] = None,
) -> bool:
    """Presence-only skip check bounded to one Qdrant point."""
    normalized = normalize_file_path(file_path)
    kwargs = {
        "collection_name": collection_name,
        "scroll_filter": rest_models.Filter(must=[
            rest_models.FieldCondition(
                key="file_path",
                match=rest_models.MatchValue(value=normalized),
            )
        ]),
        "limit": 1,
        "with_payload": False,
        "with_vectors": False,
    }
    if timeout is not None:
        kwargs["timeout"] = _qdrant_timeout(timeout)
    try:
        points, _ = client.scroll(**kwargs)
        return bool(points)
    except TypeError:
        # Small test doubles and older qdrant-client releases may not expose
        # all keyword arguments.  Keep the lookup bounded in the fallback.
        kwargs.pop("timeout", None)
        try:
            points, _ = client.scroll(**kwargs)
            return bool(points)
        except Exception:
            return False
    except Exception:
        return False


qdrant_file_exists = is_already_indexed


def check_file_exists_and_unchanged(
    client: QdrantClient,
    collection_name: str,
    file_path: str,
    modified_at_iso: Optional[str] = None,
) -> bool:
    """Legacy name retained; the new strategy intentionally ignores mtime."""
    return is_already_indexed(client, collection_name, file_path)


def delete_points_by_file_path(
    client: QdrantClient,
    collection_name: str,
    file_path: str,
    timeout: Optional[float] = None,
    raise_errors: bool = False,
) -> int:
    """Delete all points matching a path; return operation success for legacy callers."""
    normalized = normalize_file_path(file_path)
    filter_obj = rest_models.Filter(must=[
        rest_models.FieldCondition(
            key="file_path",
            match=rest_models.MatchValue(value=normalized),
        )
    ])
    kwargs = {
        "collection_name": collection_name,
        "points_selector": rest_models.FilterSelector(filter=filter_obj),
        "wait": True,
    }
    if timeout is not None:
        kwargs["timeout"] = _qdrant_timeout(timeout)
    try:
        client.delete(**kwargs)
        return 1
    except TypeError:
        kwargs.pop("timeout", None)
        try:
            client.delete(**kwargs)
            return 1
        except TypeError:
            kwargs.pop("wait", None)
            try:
                client.delete(**kwargs)
                return 1
            except Exception:
                if raise_errors:
                    raise
                return 0
        except Exception:
            if raise_errors:
                raise
            return 0
    except Exception:
        if raise_errors:
            raise
        return 0


def deterministic_point_id(file_path: str, chunk_index: int) -> str:
    """Create a stable UUID so a retry cannot duplicate a chunk."""
    seed = f"{canonical_file_path(file_path)}:{int(chunk_index)}"
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return str(uuid.UUID(digest[:32]))


def _chunk_value(chunk: Any, name: str, default: Any = None) -> Any:
    if isinstance(chunk, dict):
        return chunk.get(name, default)
    return getattr(chunk, name, default)


def build_point(
    file_path: str,
    chunk: Any,
    vector: List[float],
    classification: Optional[Dict[str, Any]] = None,
    file_name: Optional[str] = None,
    extension: Optional[str] = None,
    indexed_at: Optional[str] = None,
) -> Dict[str, Any]:
    normalized = normalize_file_path(file_path)
    payload = {
        "file_path": normalized,
        "file_name": file_name or normalized.rsplit("\\", 1)[-1].rsplit("/", 1)[-1],
        "file_extension": extension or "",
        "departments": (classification or {}).get("departments", []),
        "doc_types": (classification or {}).get("doc_types", []),
        "chunk_index": _chunk_value(chunk, "chunk_index", 0),
        "chunk_total": _chunk_value(chunk, "chunk_total", 0) or 0,
        "section_context": _chunk_value(chunk, "section_context", "") or "",
        "content": _chunk_value(chunk, "text", "") or "",
    }
    if indexed_at is not None:
        payload["indexed_at"] = indexed_at
    return {
        "id": deterministic_point_id(normalized, payload["chunk_index"]),
        "vector": vector,
        "payload": payload,
    }


def _estimate_point_bytes(point: Dict[str, Any]) -> int:
    return len(json.dumps(point, ensure_ascii=False, separators=(",", ":"), default=str).encode("utf-8"))


def iter_bounded_point_batches(
    points_data: Iterable[Dict[str, Any]],
    max_points: int = 64,
    max_bytes: int = 4 * 1024 * 1024,
) -> Iterator[List[Dict[str, Any]]]:
    """Yield raw point batches bounded by both count and serialized size."""
    if max_points < 1 or max_bytes < 1:
        raise ValueError("Point batch limits must be positive")

    batch: List[Dict[str, Any]] = []
    batch_bytes = 0
    for point in points_data:
        item = dict(point)
        if not item.get("id"):
            payload = item.get("payload") or {}
            item["id"] = deterministic_point_id(
                payload.get("file_path", ""), payload.get("chunk_index", 0)
            )
        item_bytes = _estimate_point_bytes(item)
        if item_bytes > max_bytes:
            raise ValueError("A single Qdrant point exceeds qdrant_upsert_max_bytes")
        if batch and (len(batch) >= max_points or batch_bytes + item_bytes > max_bytes):
            yield batch
            batch = []
            batch_bytes = 0
        batch.append(item)
        batch_bytes += item_bytes
    if batch:
        yield batch


def iter_point_batches(
    file_path: str,
    chunk_batch: Iterable[Any],
    vectors: Iterable[List[float]],
    classification: Optional[Dict[str, Any]] = None,
    max_points: int = 64,
    max_bytes: int = 4 * 1024 * 1024,
    file_name: Optional[str] = None,
    extension: Optional[str] = None,
    indexed_at: Optional[str] = None,
) -> Iterator[List[Dict[str, Any]]]:
    points = (
        build_point(
            file_path,
            chunk,
            vector,
            classification=classification,
            file_name=file_name,
            extension=extension,
            indexed_at=indexed_at,
        )
        for chunk, vector in zip(chunk_batch, vectors)
    )
    yield from iter_bounded_point_batches(points, max_points=max_points, max_bytes=max_bytes)


def upsert_point_batch(
    client: QdrantClient,
    collection_name: str,
    points_data: Iterable[Dict[str, Any]],
    wait: bool = True,
    timeout: Optional[float] = None,
):
    qdrant_points = [
        rest_models.PointStruct(
            id=pt["id"], vector=pt["vector"], payload=pt["payload"]
        )
        for pt in points_data
    ]
    if not qdrant_points:
        return None
    kwargs = {
        "collection_name": collection_name,
        "points": qdrant_points,
        "wait": wait,
    }
    if timeout is not None:
        kwargs["timeout"] = _qdrant_timeout(timeout)
    try:
        return client.upsert(**kwargs)
    except TypeError:
        kwargs.pop("timeout", None)
        try:
            return client.upsert(**kwargs)
        except TypeError:
            kwargs.pop("wait", None)
            return client.upsert(**kwargs)


def upsert_file_chunks(
    client: QdrantClient,
    collection_name: str,
    points_data: Iterable[Dict[str, Any]],
    max_points: int = 64,
    max_bytes: int = 4 * 1024 * 1024,
    timeout: Optional[float] = None,
):
    """Compatibility API now implemented as bounded, deterministic writes."""
    for batch in iter_bounded_point_batches(points_data, max_points=max_points, max_bytes=max_bytes):
        upsert_point_batch(client, collection_name, batch, wait=True, timeout=timeout)


def search_qdrant(
    client: QdrantClient,
    collection_name: str,
    query_vector: List[float],
    top_k: int = 50,
    departments: Optional[List[str]] = None,
    doc_types: Optional[List[str]] = None,
    extensions: Optional[List[str]] = None,
) -> List[Any]:
    must_conditions = []
    if departments:
        must_conditions.append(rest_models.FieldCondition(
            key="departments", match=rest_models.MatchAny(any=departments)
        ))
    if doc_types:
        must_conditions.append(rest_models.FieldCondition(
            key="doc_types", match=rest_models.MatchAny(any=doc_types)
        ))
    if extensions:
        must_conditions.append(rest_models.FieldCondition(
            key="file_extension", match=rest_models.MatchAny(any=extensions)
        ))
    search_filter = rest_models.Filter(must=must_conditions) if must_conditions else None
    if hasattr(client, "search"):
        return client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
        )
    return client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
        query_filter=search_filter,
        with_payload=True,
    ).points


def update_payload_for_file(
    client: QdrantClient,
    collection_name: str,
    file_path: str,
    departments: List[str],
    doc_types: List[str],
    page_size: int = 500,
    raise_errors: bool = False,
) -> int:
    """Update every matching point, not only the first scroll page."""
    updated_count = 0
    offset = None
    try:
        while True:
            kwargs = {
                "collection_name": collection_name,
                "scroll_filter": rest_models.Filter(must=[
                    rest_models.FieldCondition(
                        key="file_path",
                        match=rest_models.MatchValue(value=normalize_file_path(file_path)),
                    )
                ]),
                "limit": page_size,
                "with_payload": False,
                "with_vectors": False,
            }
            if offset is not None:
                kwargs["offset"] = offset
            records, next_offset = client.scroll(**kwargs)
            if not records:
                break
            ids = [record.id for record in records]
            client.set_payload(
                collection_name=collection_name,
                payload={"departments": departments, "doc_types": doc_types},
                points=ids,
            )
            updated_count += len(ids)
            if next_offset is None:
                break
            offset = next_offset
        return updated_count
    except Exception:
        if raise_errors:
            raise
        return 0
