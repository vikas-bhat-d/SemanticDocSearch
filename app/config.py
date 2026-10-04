import json
import secrets
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import bcrypt
from sqlalchemy.orm import Session
from app.models import Config, FileTypeConfig, Synonym


def hash_secret(secret: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(secret.encode('utf-8'), salt).decode('utf-8')


def verify_secret(secret: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(secret.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


DEFAULT_CONFIGS = {
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    "embedding_dimensions": "384",
    "parallel_workers": "4",
    "index_workers": "4",
    "index_queue_capacity": "64",
    "embedding_batch_size": "32",
    "embedding_concurrency": "1",
    "qdrant_upsert_batch_size": "64",
    "qdrant_upsert_max_bytes": "4194304",
    "qdrant_host": "localhost",
    "qdrant_port": "6333",
    "collection_name": "knowledge_base",
    "admin_username": "admin",
    "log_level": "INFO",
    "chunk_size": "512",
    "chunk_overlap": "64",
    "rows_per_chunk": "15",
    "search_top_k": "50",
    "search_per_page": "10",
    "search_excerpt_count": "3",
    "max_file_size_mb": "100",
    "max_markdown_chars": "10000000",
    "max_chunk_chars": "200000",
    "conversion_timeout_seconds": "300",
    "qdrant_timeout_seconds": "30",
    "counter_flush_interval": "25",
    "queue_put_timeout_seconds": "0.25",
    "worker_shutdown_timeout_seconds": "30",
}

DEFAULT_FILE_TYPES = [
    (".xlsx", "excel", 1),
    (".xls", "excel", 1),
    (".csv", "excel", 1),
    (".docx", "heading", 1),
    (".doc", "heading", 1),
    (".md", "heading", 1),
    (".txt", "heading", 1),
    (".pptx", "slide", 1),
    (".ppt", "slide", 1),
    (".pdf", "generic", 1),
    (".html", "generic", 1),
    (".htm", "generic", 1),
]

DEFAULT_SYNONYMS = [
    ("computer", json.dumps(["laptop", "desktop", "pc", "workstation", "machine"])),
    ("document", json.dumps(["file", "report", "doc", "record"])),
    ("invoice", json.dumps(["bill", "receipt", "voucher"])),
    ("employee", json.dumps(["staff", "worker", "personnel", "associate"])),
]


@dataclass
class ConfigData:
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimensions: int = 384
    parallel_workers: int = 4
    index_workers: int = 4
    index_queue_capacity: int = 64
    embedding_batch_size: int = 32
    embedding_concurrency: int = 1
    qdrant_upsert_batch_size: int = 64
    qdrant_upsert_max_bytes: int = 4 * 1024 * 1024
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "knowledge_base"
    admin_username: str = "admin"
    admin_password_hash: str = ""
    api_key_hash: str = ""
    log_level: str = "INFO"
    chunk_size: int = 512
    chunk_overlap: int = 64
    rows_per_chunk: int = 15
    search_top_k: int = 50
    search_per_page: int = 10
    search_excerpt_count: int = 3
    max_file_size_mb: int = 100
    max_markdown_chars: int = 10_000_000
    max_chunk_chars: int = 200_000
    conversion_timeout_seconds: float = 300.0
    qdrant_timeout_seconds: float = 30.0
    counter_flush_interval: int = 25
    queue_put_timeout_seconds: float = 0.25
    worker_shutdown_timeout_seconds: float = 30.0
    raw: Dict[str, str] = field(default_factory=dict)


_cached_config: Optional[ConfigData] = None
_raw_initial_api_key: Optional[str] = None


def _bounded_int(raw: Dict[str, str], key: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(raw.get(key, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


def _bounded_float(raw: Dict[str, str], key: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(raw.get(key, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


def seed_default_configs(db: Session) -> Optional[str]:
    """
    Seeds default configuration entries, file types, and synonyms if DB is empty.
    Returns plain initial API key if generated for the first time, otherwise None.
    """
    global _raw_initial_api_key
    initial_key = None

    # Check admin password
    admin_pass = db.query(Config).filter_by(key="admin_password_hash").first()
    if not admin_pass:
        db.add(Config(key="admin_password_hash", value=hash_secret("admin")))

    # Check API key
    api_key_row = db.query(Config).filter_by(key="api_key_hash").first()
    if not api_key_row:
        initial_key = f"sk-{secrets.token_hex(16)}"
        _raw_initial_api_key = initial_key
        db.add(Config(key="api_key_hash", value=hash_secret(initial_key)))

    # Seed remaining standard key-values
    for k, v in DEFAULT_CONFIGS.items():
        row = db.query(Config).filter_by(key=k).first()
        if not row:
            db.add(Config(key=k, value=v))

    # Seed default file types
    for ext, chunker, enabled in DEFAULT_FILE_TYPES:
        row = db.query(FileTypeConfig).filter_by(extension=ext).first()
        if not row:
            db.add(FileTypeConfig(extension=ext, chunker=chunker, enabled=enabled))

    # Seed default synonyms
    for term, syns in DEFAULT_SYNONYMS:
        row = db.query(Synonym).filter_by(term=term).first()
        if not row:
            db.add(Synonym(term=term, synonyms=syns))

    db.commit()
    return initial_key


def get_raw_initial_api_key() -> Optional[str]:
    return _raw_initial_api_key


def load_config(db: Session) -> ConfigData:
    global _cached_config
    seed_default_configs(db)

    rows = db.query(Config).all()
    raw_dict = {row.key: row.value for row in rows}

    # ``parallel_workers`` remains the persisted/UI compatibility alias.  A
    # new index_workers value takes precedence when present.
    parallel_workers = _bounded_int(raw_dict, "parallel_workers", 4, 1, 64)
    index_workers = _bounded_int(raw_dict, "index_workers", parallel_workers, 1, 64)
    config = ConfigData(
        embedding_model=raw_dict.get("embedding_model", DEFAULT_CONFIGS["embedding_model"]),
        embedding_dimensions=int(raw_dict.get("embedding_dimensions", DEFAULT_CONFIGS["embedding_dimensions"])),
        parallel_workers=parallel_workers,
        index_workers=index_workers,
        index_queue_capacity=_bounded_int(raw_dict, "index_queue_capacity", 64, 1, 10000),
        embedding_batch_size=_bounded_int(raw_dict, "embedding_batch_size", 32, 1, 4096),
        embedding_concurrency=_bounded_int(raw_dict, "embedding_concurrency", 1, 1, 16),
        qdrant_upsert_batch_size=_bounded_int(raw_dict, "qdrant_upsert_batch_size", 64, 1, 10000),
        qdrant_upsert_max_bytes=_bounded_int(raw_dict, "qdrant_upsert_max_bytes", 4 * 1024 * 1024, 1024, 128 * 1024 * 1024),
        qdrant_host=raw_dict.get("qdrant_host", DEFAULT_CONFIGS["qdrant_host"]),
        qdrant_port=int(raw_dict.get("qdrant_port", DEFAULT_CONFIGS["qdrant_port"])),
        collection_name=raw_dict.get("collection_name", DEFAULT_CONFIGS["collection_name"]),
        admin_username=raw_dict.get("admin_username", DEFAULT_CONFIGS["admin_username"]),
        admin_password_hash=raw_dict.get("admin_password_hash", ""),
        api_key_hash=raw_dict.get("api_key_hash", ""),
        log_level=raw_dict.get("log_level", DEFAULT_CONFIGS["log_level"]),
        chunk_size=int(raw_dict.get("chunk_size", DEFAULT_CONFIGS["chunk_size"])),
        chunk_overlap=int(raw_dict.get("chunk_overlap", DEFAULT_CONFIGS["chunk_overlap"])),
        rows_per_chunk=int(raw_dict.get("rows_per_chunk", DEFAULT_CONFIGS["rows_per_chunk"])),
        search_top_k=int(raw_dict.get("search_top_k", DEFAULT_CONFIGS["search_top_k"])),
        search_per_page=int(raw_dict.get("search_per_page", DEFAULT_CONFIGS["search_per_page"])),
        search_excerpt_count=int(raw_dict.get("search_excerpt_count", DEFAULT_CONFIGS["search_excerpt_count"])),
        max_file_size_mb=_bounded_int(raw_dict, "max_file_size_mb", 100, 1, 1024 * 1024),
        max_markdown_chars=_bounded_int(raw_dict, "max_markdown_chars", 10_000_000, 1, 1_000_000_000),
        max_chunk_chars=_bounded_int(raw_dict, "max_chunk_chars", 200_000, 1, 10_000_000),
        conversion_timeout_seconds=_bounded_float(raw_dict, "conversion_timeout_seconds", 300.0, 1.0, 86_400.0),
        qdrant_timeout_seconds=_bounded_float(raw_dict, "qdrant_timeout_seconds", 30.0, 1.0, 3_600.0),
        counter_flush_interval=_bounded_int(raw_dict, "counter_flush_interval", 25, 1, 10_000),
        queue_put_timeout_seconds=_bounded_float(raw_dict, "queue_put_timeout_seconds", 0.25, 0.01, 60.0),
        worker_shutdown_timeout_seconds=_bounded_float(raw_dict, "worker_shutdown_timeout_seconds", 30.0, 1.0, 3_600.0),
        raw=raw_dict
    )
    _cached_config = config
    return config


def get_config(db: Session = None) -> ConfigData:
    global _cached_config
    if _cached_config is None and db is not None:
        return load_config(db)
    if _cached_config is not None:
        return _cached_config
    if db is not None:
        return load_config(db)
    return ConfigData()


def reload_config(db: Session) -> ConfigData:
    return load_config(db)
