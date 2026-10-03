import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models


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
                distance=rest_models.Distance.COSINE
            )
        )

        # Create payload keyword indexes for fast filtering
        index_fields = ["file_path", "departments", "doc_types", "file_extension"]
        for field in index_fields:
            try:
                client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field,
                    field_schema=rest_models.PayloadSchemaType.KEYWORD
                )
            except Exception:
                pass


def check_file_exists_and_unchanged(
    client: QdrantClient,
    collection_name: str,
    file_path: str,
    modified_at_iso: str
) -> bool:
    try:
        results, _ = client.scroll(
            collection_name=collection_name,
            scroll_filter=rest_models.Filter(
                must=[
                    rest_models.FieldCondition(
                        key="file_path",
                        match=rest_models.MatchValue(value=file_path)
                    ),
                    rest_models.FieldCondition(
                        key="file_modified_at",
                        match=rest_models.MatchValue(value=modified_at_iso)
                    )
                ]
            ),
            limit=1
        )
        return len(results) > 0
    except Exception:
        return False


def delete_points_by_file_path(client: QdrantClient, collection_name: str, file_path: str) -> int:
    try:
        filter_obj = rest_models.Filter(
            must=[
                rest_models.FieldCondition(
                    key="file_path",
                    match=rest_models.MatchValue(value=file_path)
                )
            ]
        )
        res = client.delete(
            collection_name=collection_name,
            points_selector=rest_models.FilterSelector(filter=filter_obj)
        )
        return 1
    except Exception:
        return 0


def delete_points_by_folder_prefix(client: QdrantClient, collection_name: str, folder_prefix: str) -> int:
    norm_prefix = folder_prefix.replace('/', '\\').lower()
    points_to_delete = []
    offset = None

    try:
        while True:
            records, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            for r in records:
                fp = (r.payload.get("file_path") or "").replace('/', '\\').lower()
                if fp.startswith(norm_prefix):
                    points_to_delete.append(r.id)

            if next_offset is None or not records:
                break
            offset = next_offset

        if points_to_delete:
            client.delete(
                collection_name=collection_name,
                points_selector=rest_models.PointIdsList(points=points_to_delete)
            )
        return len(points_to_delete)
    except Exception:
        return 0


def upsert_file_chunks(
    client: QdrantClient,
    collection_name: str,
    points_data: List[Dict[str, Any]]
):
    qdrant_points = []
    for pt in points_data:
        pt_id = pt.get("id") or str(uuid.uuid4())
        qdrant_points.append(
            rest_models.PointStruct(
                id=pt_id,
                vector=pt["vector"],
                payload=pt["payload"]
            )
        )
    if qdrant_points:
        client.upsert(
            collection_name=collection_name,
            points=qdrant_points
        )


def search_qdrant(
    client: QdrantClient,
    collection_name: str,
    query_vector: List[float],
    top_k: int = 50,
    departments: Optional[List[str]] = None,
    doc_types: Optional[List[str]] = None,
    extensions: Optional[List[str]] = None
) -> List[Any]:
    must_conditions = []

    if departments:
        must_conditions.append(
            rest_models.FieldCondition(
                key="departments",
                match=rest_models.MatchAny(any=departments)
            )
        )
    if doc_types:
        must_conditions.append(
            rest_models.FieldCondition(
                key="doc_types",
                match=rest_models.MatchAny(any=doc_types)
            )
        )
    if extensions:
        must_conditions.append(
            rest_models.FieldCondition(
                key="file_extension",
                match=rest_models.MatchAny(any=extensions)
            )
        )

    search_filter = rest_models.Filter(must=must_conditions) if must_conditions else None

    # Handle client.search API differences cleanly
    if hasattr(client, "search"):
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True
        )
    else:
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True
        ).points

    return results


def update_payload_for_file(
    client: QdrantClient,
    collection_name: str,
    file_path: str,
    departments: List[str],
    doc_types: List[str]
) -> int:
    try:
        records, _ = client.scroll(
            collection_name=collection_name,
            scroll_filter=rest_models.Filter(
                must=[
                    rest_models.FieldCondition(
                        key="file_path",
                        match=rest_models.MatchValue(value=file_path)
                    )
                ]
            ),
            limit=500,
            with_payload=True,
            with_vectors=False
        )

        updated_count = 0
        for r in records:
            client.set_payload(
                collection_name=collection_name,
                payload={
                    "departments": departments,
                    "doc_types": doc_types
                },
                points=[r.id]
            )
            updated_count += 1

        return updated_count
    except Exception:
        return 0
