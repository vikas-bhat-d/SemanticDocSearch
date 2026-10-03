# DocSearch indexer — Full Build Plan

> **IMPLEMENTATION STATUS: FULLY IMPLEMENTED (35/35 STEPS COMPLETED)**
> All core application modules, chunkers, database schema, Qdrant operations, search engine, admin UI pages, styling, scripts, and test suite have been built according to specification.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Tech Stack](#2-tech-stack)
3. [Folder Structure](#3-folder-structure)
4. [Database Schema (SQLite)](#4-database-schema-sqlite)
5. [Qdrant Collection Design](#5-qdrant-collection-design)
6. [Configuration System](#6-configuration-system)
7. [Auth System](#7-auth-system)
8. [File Type & Chunker Registry](#8-file-type--chunker-registry)
9. [Conversion Pipeline](#9-conversion-pipeline)
10. [Chunking Strategy](#10-chunking-strategy)
11. [Embedding Pipeline](#11-embedding-pipeline)
12. [Indexer Status Lifecycle](#12-indexer-status-lifecycle)
13. [Incremental XML Processing](#13-incremental-xml-processing)
14. [Classification System](#14-classification-system)
15. [Search Engine](#15-search-engine)
16. [API Endpoints](#16-api-endpoints)
17. [Admin UI Pages](#17-admin-ui-pages)
18. [Logger](#18-logger)
19. [Testing Plan](#19-testing-plan)
20. [Build Order & Implementation Status](#20-build-order)
21. [Requirements](#21-requirements)

---

## 1. System Overview

A single FastAPI + Jinja2 application that:

- Crawls configured UNC/local folders for documents
- Converts each file to Markdown using MarkItDown
- Chunks the Markdown using file-type-aware chunkers
- Embeds chunks locally using SentenceTransformers (CPU, configurable model)
- Stores vectors + metadata in Qdrant (no file paths in SQLite — Qdrant is the source of truth)
- Exposes a search API that groups results by file and returns ranked excerpts
- Provides an admin UI for all configuration, indexing control, and monitoring
- Supports incremental indexing via admin-supplied XML change/delete lists

---

## 2. Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Web framework | FastAPI | Async, fast, clean routing |
| Template engine | Jinja2 (via FastAPI) | Admin UI, no separate frontend build |
| Vector DB | Qdrant (local, Docker or binary) | Metadata filtering, payload storage, no file path in SQLite |
| Relational DB | SQLite via SQLAlchemy (sync) | Config, run tracking, auth |
| Embeddings | SentenceTransformers | Local CPU, configurable model |
| File conversion | MarkItDown | Unified MD output for all file types |
| Chunking | Custom per-type + LangChain fallback | Accuracy over simplicity |
| Auth | Session cookie (UI) + API Key header (scheduler) | Simple, secure |
| Logging | Python `logging` + rotating file handler | Configurable level, structured fields |
| Testing | pytest + pytest-mock + FastAPI TestClient | Unit + integration |
| Task execution | Python ThreadPoolExecutor (in-process) | No separate worker infra needed |

---

## 3. Folder Structure

```
project/
├── app/
│   ├── main.py                  # FastAPI app init, router registration, lifespan
│   ├── auth.py                  # Session + API key auth logic
│   ├── config.py                # Config loader from SQLite, cached
│   ├── database.py              # SQLAlchemy engine, session factory, Base
│   ├── models.py                # All SQLAlchemy ORM models
│   ├── logger.py                # Structured logger, rotating file, level from config
│   │
│   ├── routers/
│   │   ├── auth.py              # POST /api/auth/login, /logout
│   │   ├── index.py             # POST /api/index/start, /stop, GET /status
│   │   ├── search.py            # GET /api/search
│   │   ├── config.py            # CRUD for all config entities
│   │   ├── incremental.py       # POST /api/incremental/set-xml, /preview
│   │   └── reclassify.py        # POST /api/reclassify
│   │
│   ├── indexer/
│   │   ├── runner.py            # Orchestrates full index run, manages stop flag
│   │   ├── traverser.py         # Folder walking, exclusion filtering, skip logic
│   │   ├── converter.py         # MarkItDown wrapper, per-extension dispatch
│   │   ├── chunker/
│   │   │   ├── base.py          # BaseChunker ABC, ChunkResult dataclass
│   │   │   ├── registry.py      # CHUNKER_MAP, get_chunker(extension)
│   │   │   ├── excel.py         # ExcelChunker  — sheet-aware, row-group
│   │   │   ├── heading.py       # HeadingAwareChunker — DOCX, MD, TXT
│   │   │   ├── slide.py         # SlideChunker — PPTX
│   │   │   └── generic.py       # GenericChunker — PDF, HTML, fallback
│   │   ├── embedder.py          # SentenceTransformer wrapper, batch embed
│   │   ├── qdrant_ops.py        # upsert, delete, check_exists, search, reclassify
│   │   ├── xml_parser.py        # Parse change/delete XML, convert paths
│   │   └── classifier.py        # Match file path to departments + doc types
│   │
│   ├── search/
│   │   ├── engine.py            # Query builder, result grouping, synonym expansion
│   │   └── synonyms.py          # Synonym lookup from SQLite
│   │
│   └── templates/
│       ├── base.html            # Nav, layout, flash messages
│       ├── login.html
│       ├── dashboard.html       # Run status, stats, start/stop
│       ├── folders.html         # Index folders CRUD + per-folder status
│       ├── exclusions.html      # Excluded paths and extensions
│       ├── file_types.html      # Allowed extensions + chunker assignment
│       ├── departments.html     # Department name + path patterns
│       ├── doctypes.html        # Doc type name + path patterns
│       ├── incremental.html     # XML path inputs + preview + trigger
│       ├── synonyms.html        # Synonym dictionary CRUD
│       ├── settings.html        # Model, dimensions, workers, log level, auth
│       └── logs.html            # Live log tail, filter by level/run
│
├── static/
│   ├── css/
│   │   └── app.css              # Clean light UI, large buttons, status colors
│   └── js/
│       └── app.js               # SSE log stream, status polling, copy-to-clipboard
│
├── tests/
│   ├── conftest.py              # In-memory SQLite, Qdrant mock, TestClient, auth fixtures
│   ├── test_auth.py
│   ├── test_search.py
│   ├── test_indexer/
│   │   ├── test_runner.py
│   │   ├── test_traverser.py
│   │   ├── test_converter.py
│   │   ├── test_chunker_excel.py
│   │   ├── test_chunker_heading.py
│   │   ├── test_chunker_slide.py
│   │   ├── test_chunker_generic.py
│   │   ├── test_embedder.py
│   │   ├── test_qdrant_ops.py
│   │   ├── test_xml_parser.py
│   │   └── test_classifier.py
│   ├── test_routers/
│   │   ├── test_index.py
│   │   ├── test_search.py
│   │   ├── test_config.py
│   │   ├── test_incremental.py
│   │   └── test_reclassify.py
│   └── test_search/
│       ├── test_engine.py
│       └── test_synonyms.py
│
├── data/
│   └── config.db                # SQLite DB (auto-created on first run)
│
├── logs/
│   └── app.log                  # Rotating log file
│
└── requirements.txt
```

---

## 4. Database Schema (SQLite)

### `config` — flat key-value for system settings

```sql
CREATE TABLE config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

Default rows inserted on first run:

| key | default value |
|---|---|
| `embedding_model` | `sentence-transformers/all-MiniLM-L6-v2` |
| `embedding_dimensions` | `384` |
| `parallel_workers` | `4` |
| `qdrant_host` | `localhost` |
| `qdrant_port` | `6333` |
| `collection_name` | `knowledge_base` |
| `admin_username` | `admin` |
| `admin_password_hash` | `<bcrypt of 'admin'>` |
| `api_key_hash` | `<bcrypt of generated key>` |
| `log_level` | `INFO` |
| `chunk_size` | `512` |
| `chunk_overlap` | `64` |
| `rows_per_chunk` | `15` |
| `search_top_k` | `50` |
| `search_per_page` | `10` |
| `search_excerpt_count` | `3` |

---

### `index_folders` — folders configured for indexing

```sql
CREATE TABLE index_folders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    path        TEXT NOT NULL UNIQUE,
    status      TEXT NOT NULL DEFAULT 'pending',
    -- pending | indexing | completed | failed | stopped | excluded
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

### `excluded_paths` — paths and extensions to skip

```sql
CREATE TABLE excluded_paths (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    value   TEXT NOT NULL,           -- path prefix OR extension like ".tmp"
    type    TEXT NOT NULL            -- 'path' | 'extension'
);
```

---

### `file_type_config` — allowed extensions + chunker assignment

```sql
CREATE TABLE file_type_config (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    extension    TEXT NOT NULL UNIQUE,  -- ".xlsx", ".docx", ".pdf" etc
    chunker      TEXT NOT NULL,         -- 'excel' | 'heading' | 'slide' | 'generic'
    enabled      INTEGER NOT NULL DEFAULT 1   -- 0 = skip this extension entirely
);
```

Default rows:

| extension | chunker | enabled |
|---|---|---|
| `.xlsx` | `excel` | 1 |
| `.xls` | `excel` | 1 |
| `.csv` | `excel` | 1 |
| `.docx` | `heading` | 1 |
| `.doc` | `heading` | 1 |
| `.md` | `heading` | 1 |
| `.txt` | `heading` | 1 |
| `.pptx` | `slide` | 1 |
| `.ppt` | `slide` | 1 |
| `.pdf` | `generic` | 1 |
| `.html` | `generic` | 1 |
| `.htm` | `generic` | 1 |

Admin can add new extensions, assign any chunker, enable/disable.

---

### `departments` — department config

```sql
CREATE TABLE departments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL UNIQUE,
    path_patterns    TEXT NOT NULL   -- JSON array of glob patterns
                                     -- e.g. ["*\\HR\\*", "*\\Human Resources\\*"]
);
```

---

### `doc_types` — document type config

```sql
CREATE TABLE doc_types (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL UNIQUE,   -- "CL" | "FAQ" | "DOC" | "other"
    path_patterns    TEXT NOT NULL           -- JSON array of glob patterns
);
```

---

### `synonyms` — configurable synonym dictionary

```sql
CREATE TABLE synonyms (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    term     TEXT NOT NULL UNIQUE,      -- canonical term, lowercase
    synonyms TEXT NOT NULL              -- JSON array e.g. ["laptop","desktop","pc","workstation"]
);
```

---

### `index_runs` — one row per indexing session

```sql
CREATE TABLE index_runs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    stopped_at          DATETIME,
    status              TEXT NOT NULL DEFAULT 'running',
    -- running | completed | stopped | failed
    changed_xml_path    TEXT,           -- path to changed XML for this run
    deleted_xml_path    TEXT,           -- path to deleted XML for this run
    total_files         INTEGER DEFAULT 0,
    indexed_files       INTEGER DEFAULT 0,
    skipped_files       INTEGER DEFAULT 0,
    failed_files        INTEGER DEFAULT 0,
    deleted_files       INTEGER DEFAULT 0
);
```

---

### `index_run_files` — per-file tracking within a run

```sql
CREATE TABLE index_run_files (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id          INTEGER NOT NULL REFERENCES index_runs(id),
    file_path       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    -- pending | converting | chunking | embedding | indexing | completed | failed | skipped
    chunks_indexed  INTEGER DEFAULT 0,
    error_message   TEXT,
    started_at      DATETIME,
    completed_at    DATETIME
);

CREATE INDEX idx_run_files_run_id ON index_run_files(run_id);
CREATE INDEX idx_run_files_status ON index_run_files(status);
```

---

### `incremental_xml_config` — last set XML paths (persisted for next run)

```sql
CREATE TABLE incremental_xml_config (
    id                  INTEGER PRIMARY KEY CHECK (id = 1),  -- singleton
    changed_xml_path    TEXT,
    deleted_xml_path    TEXT,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 5. Qdrant Collection Design

### Collection name: configured in `config` table (default: `knowledge_base`)

### Vector config

```python
VectorParams(
    size=<embedding_dimensions from config>,
    distance=Distance.COSINE
)
```

### Point structure (one point = one chunk)

```json
{
  "id": "<uuid4>",
  "vector": [0.1, 0.2, ...],
  "payload": {
    "file_path":         "\\\\pc135\\D\\HR\\policy.docx",
    "file_name":         "policy.docx",
    "file_extension":    ".docx",
    "departments":       ["HR", "Legal"],
    "doc_types":         ["FAQ", "CL"],
    "chunk_index":       3,
    "chunk_total":       12,
    "section_context":   "Section: Leave Policy",
    "content":           "...chunk text...",
    "file_modified_at":  "2024-01-01T00:00:00",
    "indexed_at":        "2024-01-02T10:30:00",
    "file_hash":         "sha256:abc123..."
  }
}
```

### Payload indexes (for fast filtering without vector search)

```python
# Create these on collection init
client.create_payload_index(collection, "file_path",      PayloadSchemaType.KEYWORD)
client.create_payload_index(collection, "departments",    PayloadSchemaType.KEYWORD)
client.create_payload_index(collection, "doc_types",      PayloadSchemaType.KEYWORD)
client.create_payload_index(collection, "file_extension", PayloadSchemaType.KEYWORD)
```

### Skip logic

Before indexing a file, query Qdrant:
```python
# Check if file already indexed with same modified time
results = client.scroll(
    collection,
    scroll_filter=Filter(must=[
        FieldCondition(key="file_path", match=MatchValue(value=file_path)),
        FieldCondition(key="file_modified_at", match=MatchValue(value=modified_at_iso))
    ]),
    limit=1
)
# If results not empty → skip this file
```

---

## 6. Configuration System

### `app/config.py`

- On startup: load all key-value rows from `config` table into a `Config` dataclass (cached in memory)
- Expose `get_config()` → returns cached instance
- Expose `reload_config()` → re-reads from DB (called after settings save)
- Logger level is set from config on startup and on reload

### Configurable parameters (editable in Settings UI)

| Parameter | UI Label | Notes |
|---|---|---|
| `embedding_model` | Model name | HuggingFace model ID |
| `embedding_dimensions` | Vector dimensions | Must match model output |
| `parallel_workers` | Parallel workers | Thread count for embedding |
| `qdrant_host` | Qdrant host | |
| `qdrant_port` | Qdrant port | |
| `collection_name` | Collection name | Changing this = new collection |
| `log_level` | Log level | DEBUG / INFO / WARNING / ERROR |
| `chunk_size` | Chunk size (tokens) | For heading + generic chunkers |
| `chunk_overlap` | Chunk overlap (tokens) | |
| `rows_per_chunk` | Rows per chunk | For Excel chunker |
| `search_top_k` | Search top-K | Chunks fetched before grouping |
| `search_per_page` | Results per page | Default 10 |
| `search_excerpt_count` | Excerpts per file | Top N chunks shown per result |

**Warning shown in UI:** Changing `embedding_model` or `embedding_dimensions` invalidates the existing Qdrant collection. Admin must re-index everything.

---

## 7. Auth System

### Two auth modes

**Mode 1: Session cookie (Admin UI)**
- `POST /api/auth/login` with `username` + `password` form fields
- Verify against `admin_username` + `admin_password_hash` from config
- On success: set signed session cookie (using `itsdangerous` or `starlette.middleware.sessions`)
- All UI routes check session cookie via dependency `require_session()`

**Mode 2: API Key header (Scheduler / external)**
- Pass `X-API-Key: <key>` header
- Verify against `api_key_hash` from config
- Used by `/api/index/start` and `/api/index/stop`
- Both endpoints accept either session cookie OR API key

### Auth dependency

```python
async def require_auth(
    request: Request,
    x_api_key: str = Header(None)
):
    # Check API key first
    if x_api_key and verify_api_key(x_api_key):
        return AuthContext(type="api_key")
    # Then check session
    if request.session.get("authenticated"):
        return AuthContext(type="session")
    raise HTTPException(401)
```

### Password change

- Via Settings UI only
- Hashed with `bcrypt` before storing in `config` table

### API key management

- Generated once on first run, shown once in Settings UI
- Admin can regenerate (invalidates old key)
- Stored as bcrypt hash in `config` table

---

## 8. File Type & Chunker Registry

### Admin UI: File Types page

Shows a table of all configured extensions. For each row:
- Extension (e.g. `.xlsx`)
- Chunker (dropdown: `excel`, `heading`, `slide`, `generic`)
- Enabled toggle
- Delete button

Add new row: text input for extension + chunker dropdown + Add button.

### Available chunkers (dropdown options)

| Value | Label | Best for |
|---|---|---|
| `excel` | Excel / Tabular | .xlsx, .xls, .csv |
| `heading` | Heading-Aware | .docx, .doc, .md, .txt |
| `slide` | Slide-Based | .pptx, .ppt |
| `generic` | Generic (Recursive) | .pdf, .html, anything else |

### `chunker/registry.py`

```python
CHUNKER_CLASSES = {
    "excel":   ExcelChunker,
    "heading": HeadingAwareChunker,
    "slide":   SlideChunker,
    "generic": GenericChunker,
}

def get_chunker(extension: str, db: Session) -> BaseChunker:
    """
    Look up file_type_config in DB for this extension.
    If found and enabled: return the mapped chunker class instance.
    If not found or disabled: return None (file will be skipped).
    """
    row = db.query(FileTypeConfig).filter_by(
        extension=extension.lower(), enabled=True
    ).first()
    if not row:
        return None
    return CHUNKER_CLASSES[row.chunker]()
```

During traversal: if `get_chunker()` returns `None`, file is skipped and logged as `skipped (unsupported extension)`.

---

## 9. Conversion Pipeline

### `indexer/converter.py`

```
file_path → MarkItDown.convert(file_path) → raw Markdown string
```

- MarkItDown handles: xlsx, docx, pptx, pdf, html, txt, md, csv
- If conversion raises exception: mark file as `failed`, log error, continue
- No intermediate files written to disk — everything stays in memory

### Special handling

**Excel files:** MarkItDown is called with `xlsx_no_header=False` (default) — it produces `## SheetName` headers before each sheet's table. This is what the ExcelChunker expects.

**Password-protected files:** Will raise exception → marked `failed`, logged with message "file is password protected or corrupted."

**Empty files:** If converted MD is blank or whitespace-only → marked `skipped`, logged.

**File size guard:** If file size > configurable limit (default 100MB), skip and log warning. Add `max_file_size_mb` to config.

---

## 10. Chunking Strategy

### `chunker/base.py`

```python
@dataclass
class ChunkResult:
    text:            str    # full text to embed (includes context prefix)
    chunk_index:     int    # 0-based
    chunk_total:     int    # filled after all chunks produced
    section_context: str    # "Sheet: RN_WebView" / "Section: React Native WebView 1" / "Slide 3"

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, md_text: str, file_name: str) -> list[ChunkResult]:
        ...
```

---

### Chunker 1: ExcelChunker (`.xlsx`, `.xls`, `.csv`)

**Input:** Full MarkItDown MD output (multiple `## SheetName` sections)

**Per-sheet steps:**

```
1. Split on "## " to extract sheets
2. For each sheet:
   a. Parse the markdown table rows
   b. Drop rows where ALL cells are NaN or empty string
   c. Replace remaining NaN with ""
   d. Drop columns where ALL values are empty across entire sheet
   e. Keep first row of sheet as "anchor row" (prepended to every chunk)
   f. Group remaining rows into batches of `rows_per_chunk` (default 15)
   g. Last 2 rows of previous batch prepended to next batch (overlap)
   h. Each chunk text:
      "[Sheet: {sheet_name}]\n{anchor_row}\n{row_batch}"
3. section_context = "Sheet: {sheet_name}"
```

**CSV:** No `##` separators — treat entire file as one sheet named after the file.

---

### Chunker 2: HeadingAwareChunker (`.docx`, `.doc`, `.md`, `.txt`)

**Input:** Full MarkItDown MD output

**Steps:**

```
1. Split on H1 headings (lines starting with "# ")
   — H2 headings ("## ") within a section are treated as sub-context, not split points
   — If no H1 headings found, treat entire document as one section
2. For each section (heading + its content):
   a. If section <= chunk_size tokens: one chunk, keep as-is
   b. If section > chunk_size tokens:
      - Apply RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
      - Prepend "[Section: {heading_text}]" to each sub-chunk
   c. Tables within a section: never split mid-table
      - If a table alone exceeds chunk_size: keep as one chunk (do not split)
   d. Code blocks: never split mid-code-block
      - If a code block alone exceeds chunk_size: keep as one chunk
3. section_context = "Section: {heading_text}" or "Document: {file_name}" if no headings
```

---

### Chunker 3: SlideChunker (`.pptx`, `.ppt`)

**Input:** Full MarkItDown MD output

**Steps:**

```
1. Split on "<!-- Slide number: N -->" markers
2. Each slide = one chunk
   - Visible text + "### Notes:" content are merged into one block
   - Prepend "[Slide N of Total]"
3. If a single slide exceeds chunk_size tokens (rare):
   - Split on sentence boundaries (". ") only — never mid-sentence
4. section_context = "Slide {N}"
```

---

### Chunker 4: GenericChunker (`.pdf`, `.html`, fallback)

**Input:** Full MarkItDown MD output (plain prose)

**Steps:**

```
1. Apply RecursiveCharacterTextSplitter(
       separators=["\n\n", "\n", ". ", " "],
       chunk_size=chunk_size,
       chunk_overlap=chunk_overlap
   )
2. No structural preprocessing
3. section_context = "" (empty — no structure available)
```

---

### Chunk size units

All `chunk_size` and `chunk_overlap` values are in **tokens**, estimated as `len(text.split())` (word count). Not character count, not subword tokens. Simple and fast — sufficient for 512 token targets.

---

## 11. Embedding Pipeline

### `indexer/embedder.py`

```python
class Embedder:
    def __init__(self, model_name: str, dimensions: int):
        self.model = SentenceTransformer(model_name)
        self.dimensions = dimensions

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        vectors = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return vectors.tolist()
```

- Model loaded once at run start, shared across all workers
- `normalize_embeddings=True` ensures cosine similarity works correctly
- Model is loaded from HuggingFace cache (downloaded on first use)

### Parallel embedding

- `runner.py` uses `ThreadPoolExecutor(max_workers=parallel_workers)`
- Each worker handles one file at a time (convert → chunk → embed → upsert)
- Embedding itself is called per-file (all chunks of one file embedded in one `embed_batch` call)
- Workers share the same `Embedder` instance (SentenceTransformer is thread-safe for inference)

### Stop signal check

After each file completes (or fails), runner checks `stop_flag` before picking up next file from queue.

---

## 12. Indexer Status Lifecycle

### Run-level states

```
[IDLE] ─── start ──► [RUNNING] ─── all files done ──► [COMPLETED]
                          │
                      stop signal
                          │
                          ▼
                      [STOPPING]    ← in-progress file finishes or is rolled back
                          │
                          ▼
                      [STOPPED]     ← written to DB, next start resumes
                          │
                      start again
                          │
                          ▼
                      [RUNNING]     ← resumes from pending files
```

Only one run can be RUNNING at a time. Start button is disabled if a run is RUNNING or STOPPING.

---

### File-level states (within a run)

```
[pending]
    │
    ▼
[converting]        ← MarkItDown conversion in progress
    │
    ▼
[chunking]          ← Chunker splitting the MD
    │
    ▼
[embedding]         ← SentenceTransformer encoding
    │
    ▼
[indexing]          ← Qdrant upsert in progress
    │
    ├── success ──► [completed]
    └── error   ──► [failed]      ← error_message stored

[skipped]           ← file unchanged, extension disabled, empty, too large
```

---

### Stop behavior (critical)

```
1. Admin clicks Stop (or POST /api/index/stop)
2. stop_flag is set to True in memory (threading.Event)
3. Run status updated to 'stopping' in DB
4. Workers: after current file finishes, check stop_flag before next file
5. If stop_flag is set mid-file:
   a. File completes its current stage normally (do not interrupt mid-embed)
   b. After stage completes, check stop_flag
   c. If set: delete all Qdrant points for this file (clean rollback)
   d. Mark file as 'pending' in index_run_files
   e. Stop picking up new files
6. Once all workers have stopped:
   a. Run status → 'stopped'
   b. stopped_at → now()
7. Next run: if the immediately previous run was stopped, picks up its files
   with status='pending' first,
   then continues folder traversal for not-yet-seen files
```

---

### Resume logic (on next run start)

```python
def get_files_to_index(db, run_id, folders, excluded_paths):
    # Phase 1: Resume pending files only from the immediately previous run
    previous_run = db.query(IndexRun).filter(IndexRun.id < run_id)
                     .order_by(desc('id')).first()
    if previous_run and previous_run.status == 'stopped':
        pending = db.query(IndexRunFile)
                    .filter_by(run_id=previous_run.id, status='pending')
                    .all()
        yield from [f.file_path for f in pending]

    # Phase 2: Traverse configured folders
    yield from traverser.walk(folders, excluded_paths, db)
    # traverser.walk skips files already completed in Qdrant (unchanged)
```

---

### Dashboard status indicators

| State | Color | Label |
|---|---|---|
| IDLE | Grey | No active run |
| RUNNING | Blue (pulsing) | Indexing in progress |
| STOPPING | Yellow | Stopping... |
| STOPPED | Orange | Stopped (resumable) |
| COMPLETED | Green | Last run completed |
| FAILED | Red | Last run failed |

Progress bar: `indexed_files / total_files * 100%`
Live counters: indexed / skipped / failed / deleted

---

## 13. Incremental XML Processing

### XML format (provided by admin)

```xml
<NewDataSet>
  <FILELIST>
    <Type>FILE</Type>
    <Value>E:\Winman Backup\Daily_INCREMENTAL(1)\Final-16-Jul-2015\PC135(D.)\Desktop\file.xlsx</Value>
  </FILELIST>
</NewDataSet>
```

Only `FILE` entries are supported. `FOLDER` entries and any other entry types
are ignored so an incremental run never deletes or reindexes an entire folder.

### Path conversion logic

**Input:** `E:\Winman Backup\Daily_INCREMENTAL(1)\Final-16-Jul-2015\PC135(D.)\Desktop\file.xlsx`

**Algorithm:**

```python
import re

def convert_backup_path(backup_path: str) -> str:
    """
    Finds the segment matching pattern MACHINENAME(DRIVELETTER.)
    e.g. PC135(D.) → machine=pc135, drive=D
    Everything after that segment becomes the UNC path.
    """
    # Pattern: word chars, then (single_letter.)
    pattern = re.compile(r'([A-Za-z0-9_-]+)\(([A-Za-z])\.\)')
    
    parts = backup_path.replace('/', '\\').split('\\')
    
    for i, part in enumerate(parts):
        match = pattern.fullmatch(part)
        if match:
            machine = match.group(1).lower()       # "pc135"
            drive   = match.group(2).upper()       # "D"
            rest    = '\\'.join(parts[i+1:])       # "Desktop\file.xlsx"
            return f"\\\\{machine}\\{drive}\\{rest}"
    
    # No pattern found — return as-is with warning log
    return backup_path
```

**Output:** `\\pc135\D\Desktop\file.xlsx`

### Processing flow on run start

```
1. Parse changed_xml_path → file-only list of `(FILE, converted_path)` tuples
2. Parse deleted_xml_path → file-only list of `(FILE, converted_path)` tuples
3. For each file path in both lists, delete Qdrant points where
   `file_path == converted_path`
4. Log: "Deleted N points for M files from changed/deleted XML"
5. Update run: deleted_files = count of files processed
6. Continue to normal folder traversal
   — files deleted in step 3 will now appear as "not in Qdrant" and get re-indexed
```

### Incremental UI page

- Two path input fields: "Changed XML path" and "Deleted XML path"
- Save button (persists to `incremental_xml_config` table)
- Preview button: parses XML and shows list of paths that will be affected (without deleting)
- On run start, these paths are automatically used if set

---

## 14. Classification System

### `indexer/classifier.py`

```python
import fnmatch

def classify_file(file_path: str, db: Session) -> dict:
    """
    Returns {"departments": [...], "doc_types": [...]}
    Both lists can be empty (file is still indexed, just unclassified).
    One file can match multiple departments and multiple doc types.
    """
    departments = []
    doc_types   = []

    path_normalized = file_path.replace('/', '\\').lower()

    for dept in db.query(Department).all():
        patterns = json.loads(dept.path_patterns)
        for pattern in patterns:
            if fnmatch.fnmatch(path_normalized, pattern.lower()):
                departments.append(dept.name)
                break  # one match is enough for this dept

    for dt in db.query(DocType).all():
        patterns = json.loads(dt.path_patterns)
        for pattern in patterns:
            if fnmatch.fnmatch(path_normalized, pattern.lower()):
                doc_types.append(dt.name)
                break

    return {"departments": departments, "doc_types": doc_types}
```

### Pattern examples (configured in UI)

**Departments:**
- HR: `*\\hr\\*`, `*\\human resources\\*`
- Finance: `*\\finance\\*`, `*\\accounts\\*`

**Doc Types:**
- FAQ: `*\\faq\\*`, `*faq*`
- CL: `*\\circular\\*`, `*\\cl\\*`

### Reclassification (without re-embedding)

```
POST /api/reclassify
Body: { "file_path": "\\pc135\D\HR\policy.docx", "departments": ["HR"], "doc_types": ["CL"] }

Action:
1. Scroll Qdrant for all points where file_path == given path
2. For each point: client.set_payload(collection, {"departments": [...], "doc_types": [...]}, [point_id])
3. No re-embedding, no chunk changes
4. Returns: { "updated_points": N }
```

---

## 15. Search Engine

### `search/engine.py`

### Request parameters

| Param | Type | Description |
|---|---|---|
| `q` | string | Search query (required) |
| `department` | string (multi) | Filter by department name |
| `doc_type` | string (multi) | Filter by doc type |
| `extension` | string (multi) | Filter by file extension |
| `page` | int | Page number (default 1) |
| `per_page` | int | Results per page (default 10) |
| `exact` | bool | If true, search `q` as exact phrase (quoted search) |

URL example: `/api/search?q=computer&department=HR&doc_type=FAQ&page=1`

---

### Search pipeline

```
Step 1: Synonym expansion
   - Look up q in synonyms table
   - Expanded query = original terms + synonym terms
   - e.g. "computer" → "computer laptop desktop PC workstation"
   - Log synonyms_used list for response

Step 2: Embed the expanded query
   - Use same Embedder instance (or lazy-load for search)
   - Single encode call

Step 3: Qdrant vector search
   - search(
         collection,
         query_vector=query_embedding,
         limit=search_top_k,           ← fetch top 50 chunks (configurable)
         query_filter=Filter(must=[
             FieldCondition("departments", MatchAny(departments)) if departments,
             FieldCondition("doc_types",   MatchAny(doc_types))   if doc_types,
             FieldCondition("file_extension", MatchAny(extensions)) if extensions,
         ]),
         with_payload=True
     )

Step 4: Group by file
   - results_map: dict[file_path → list of (score, chunk)]
   - For each chunk result: add to its file's list

Step 5: Score each file
   - file_score = max(chunk scores for that file)   ← best chunk wins
   - Sort files by file_score descending

Step 6: Exact phrase boost (if q contains quotes or exact=true)
   - After vector search, re-score: if exact phrase appears in chunk content → boost score by 0.2
   - Re-sort after boost

Step 7: Select top excerpts per file
   - For each file: sort its chunks by score descending
   - Take top search_excerpt_count chunks as excerpts
   - Highlight query terms in each excerpt (wrap with <mark> tags)

Step 8: Paginate
   - Total unique files = len(results_map)
   - Slice: results[((page-1)*per_page) : (page*per_page)]

Step 9: Build response
```

---

### Search response shape

```json
{
  "results": [
    {
      "file_name":    "policy.docx",
      "file_path":    "\\\\pc135\\D\\HR\\policy.docx",
      "file_extension": ".docx",
      "departments":  ["HR"],
      "doc_types":    ["CL"],
      "score":        0.91,
      "excerpts": [
        {
          "text":            "...matched chunk text with <mark>computer</mark>...",
          "chunk_index":     3,
          "section_context": "Section: Leave Policy"
        },
        {
          "text":            "...second best chunk...",
          "chunk_index":     7,
          "section_context": "Section: IT Equipment"
        }
      ]
    }
  ],
  "total_files":   199,
  "total_pages":   20,
  "page":          1,
  "per_page":      10,
  "query":         "computer",
  "synonyms_used": ["laptop", "desktop", "PC", "workstation"],
  "exact_mode":    false
}
```

---

### Quoted / exact search

If `q` contains `"..."` (double quotes) or `exact=true` param is set:
- Extract the phrase from quotes
- After vector search, filter results to only those where the exact phrase appears in `content` (case-insensitive substring match)
- No synonym expansion for the quoted portion
- UI shows "Exact match mode" indicator

---

### Synonym dictionary (admin managed)

- Stored in `synonyms` table: `term` (canonical) → `synonyms` (JSON array)
- Admin can add/edit/delete entries via Synonyms UI page
- Seeded defaults on first run:

| term | synonyms |
|---|---|
| `computer` | `["laptop", "desktop", "pc", "workstation", "machine"]` |
| `document` | `["file", "report", "doc", "record"]` |
| `invoice` | `["bill", "receipt", "voucher"]` |
| `employee` | `["staff", "worker", "personnel", "associate"]` |

Expansion logic: for each word in query, look up in synonyms table. Append synonyms to query string. Duplicates removed.

---

## 16. API Endpoints

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | None | Login with username + password |
| POST | `/api/auth/logout` | Session | Clear session |

---

### Indexer control

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/index/start` | Session or API Key | Start indexing run |
| POST | `/api/index/stop` | Session or API Key | Stop current run |
| GET | `/api/index/status` | Session or API Key | Current run status + live counters |
| GET | `/api/index/runs` | Session | List past runs (paginated) |
| GET | `/api/index/runs/{run_id}/files` | Session | Files in a run (paginated, filterable by status) |

`/api/index/start` accepts optional body:
```json
{ "changed_xml_path": "/path/to/changed.xml", "deleted_xml_path": "/path/to/deleted.xml" }
```
If omitted, uses last saved `incremental_xml_config`.

---

### Search

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/search` | None (public) | Search with filters and pagination |

---

### Configuration

| Method | Path | Auth | Description |
|---|---|---|---|
| GET/PUT | `/api/config/settings` | Session | Get/update system settings |
| GET | `/api/config/folders` | Session | List index folders |
| POST | `/api/config/folders` | Session | Add folder |
| DELETE | `/api/config/folders/{id}` | Session | Remove folder |
| GET | `/api/config/exclusions` | Session | List exclusions |
| POST | `/api/config/exclusions` | Session | Add exclusion |
| DELETE | `/api/config/exclusions/{id}` | Session | Remove exclusion |
| GET | `/api/config/file-types` | Session | List file type configs |
| POST | `/api/config/file-types` | Session | Add file type |
| PUT | `/api/config/file-types/{id}` | Session | Update chunker/enabled |
| DELETE | `/api/config/file-types/{id}` | Session | Remove file type |
| GET | `/api/config/departments` | Session | List departments |
| POST | `/api/config/departments` | Session | Add department |
| PUT | `/api/config/departments/{id}` | Session | Update |
| DELETE | `/api/config/departments/{id}` | Session | Delete |
| GET | `/api/config/doc-types` | Session | List doc types |
| POST | `/api/config/doc-types` | Session | Add doc type |
| PUT | `/api/config/doc-types/{id}` | Session | Update |
| DELETE | `/api/config/doc-types/{id}` | Session | Delete |
| GET | `/api/config/synonyms` | Session | List synonyms |
| POST | `/api/config/synonyms` | Session | Add synonym entry |
| PUT | `/api/config/synonyms/{id}` | Session | Update |
| DELETE | `/api/config/synonyms/{id}` | Session | Delete |

---

### Incremental

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/incremental/config` | Session | Get saved XML paths |
| POST | `/api/incremental/config` | Session | Save XML paths |
| POST | `/api/incremental/preview` | Session | Parse XML, return affected paths without deleting |

---

### Reclassify

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/reclassify` | Session | Update departments + doc_types in Qdrant for a file |

---

### Logs

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/logs/stream` | Session | SSE stream of live log lines |
| GET | `/api/logs/history` | Session | Last N log lines from file (paginated) |

---

## 17. Admin UI Pages

All pages extend `base.html`. Navigation sidebar always visible. Flash messages on action success/failure.

---

### Dashboard (`/`)

- Current run status badge (color + label)
- Progress bar: `indexed / total files`
- Live counters: Indexed / Skipped / Failed / Deleted (auto-refresh every 3s via JS polling `/api/index/status`)
- Start button (disabled if running/stopping)
- Stop button (disabled if not running)
- Last run summary: start time, end time, totals
- Link to current run's file list

---

### Folders (`/folders`)

Table of configured index folders with columns: Path, Status, Last Updated, Actions (Remove).

- Add folder: text input for UNC/local path + Add button
- Each row shows folder status badge
- Click folder path → opens run files filtered to that folder prefix

---

### File Types (`/file-types`)

Table of extension configs: Extension, Chunker (dropdown, inline editable), Enabled (toggle), Delete.

- Add row: Extension input (e.g. `.xlsx`) + Chunker dropdown + Add button
- Chunker dropdown options: Excel / Heading-Aware / Slide-Based / Generic
- Disabled extensions shown greyed out

---

### Exclusions (`/exclusions`)

Two sections: Excluded Paths and Excluded Extensions.

- Excluded paths: list of path prefixes with Delete buttons. Add: text input.
- Excluded extensions: list of extensions (e.g. `.tmp`, `.log`) with Delete buttons. Add: text input.

---

### Departments (`/departments`)

Table: Name, Path Patterns (comma-separated), Edit, Delete.

- Add: Name input + Patterns textarea (one pattern per line) + Add button
- Edit inline or via modal
- Patterns use glob syntax (`*\HR\*`), shown with examples

---

### Doc Types (`/doc-types`)

Same layout as Departments.

---

### Synonyms (`/synonyms`)

Table: Term, Synonyms (comma-separated), Edit, Delete.

- Add: Term input + Synonyms input (comma-separated) + Add button
- Used at search time for query expansion

---

### Incremental (`/incremental`)

- "Changed XML path" text input (points to local/UNC XML file)
- "Deleted XML path" text input
- Save button (persists)
- Preview button: parses XML, shows table of affected paths (type, original path, converted path)
- Status message: "Last processed: N files on [date]"

---

### Settings (`/settings`)

Grouped sections:

**Embedding**
- Model name (text input)
- Dimensions (number input)
- Warning: "Changing model requires full re-index"

**Indexing**
- Parallel workers (number, 1-16)
- Max file size MB (number)
- Chunk size (tokens)
- Chunk overlap (tokens)
- Rows per chunk (for Excel)

**Search**
- Top-K chunks
- Results per page
- Excerpts per file

**Qdrant**
- Host
- Port
- Collection name

**Logging**
- Log level dropdown (DEBUG / INFO / WARNING / ERROR)

**Auth**
- Change admin password (old + new + confirm)
- Regenerate API key (shows new key once, copy button)

---

### Logs (`/logs`)

- Log level filter dropdown
- Run ID filter (optional)
- Live tail toggle (SSE stream via `/api/logs/stream`)
- Log table: timestamp, level (color-coded badge), module, run_id, file_path, message
- Pause/resume stream button
- Download last 1000 lines button

---

## 18. Logger

### `app/logger.py`

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logger(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("deptwise")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    ))

    # Rotating file handler: 10MB max, 5 backups
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s | run=%(run_id)s | file=%(file_path)s | %(message)s"
    ))

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger
```

### Structured log fields via LoggerAdapter

```python
class IndexLogger:
    def __init__(self, base_logger, run_id=None, file_path=None):
        self.extra = {"run_id": run_id or "-", "file_path": file_path or "-"}
        self.logger = logging.LoggerAdapter(base_logger, self.extra)
```

Used throughout: `log.info("Converting file")`, `log.error("Embed failed: %s", err)`

### Log level hot-reload

On settings save: call `logging.getLogger("deptwise").setLevel(new_level)` — takes effect immediately without restart.

---

## 19. Testing Plan

### `tests/conftest.py`

- `db_session`: in-memory SQLite with all tables created and seeded defaults
- `mock_qdrant`: mock of `QdrantClient` — intercepts upsert, search, delete, scroll
- `mock_embedder`: returns fixed-size zero vectors (no model loaded in tests)
- `client`: FastAPI `TestClient` with session cookie injected
- `api_key_client`: TestClient with `X-API-Key` header

---

### Unit tests

**`test_xml_parser.py`**
- Path with `PC135(D.)` → correct UNC output
- Path with `SERVER01(C.)` → correct output
- No machine pattern → returned as-is with warning
- FOLDER type → ignored
- FILE type → correct full path
- Duplicate paths → handled idempotently

**`test_classifier.py`**
- File in `*\HR\*` → department HR assigned
- File matching multiple patterns → multiple departments
- File matching no patterns → empty lists
- Case-insensitive matching

**`test_chunker_excel.py`**
- Sheet with all-NaN rows → rows dropped
- Sheet with real headers → anchor row prepended to every chunk
- Sheet with no headers (Dump-style) → first row used as anchor
- Row count > rows_per_chunk → correct number of chunks produced
- Overlap: last 2 rows of chunk N appear at start of chunk N+1
- CSV input → treated as single sheet named after file

**`test_chunker_heading.py`**
- Doc with H1 headings → one chunk per section
- Long section → split by RecursiveCharacterTextSplitter, heading prepended to each
- Section with table → table not split mid-row
- Code block not split
- No headings → one chunk with file_name as context

**`test_chunker_slide.py`**
- 8 slides → 8 chunks
- Slide text + notes merged
- Slide number in context prefix

**`test_chunker_generic.py`**
- Long prose → RecursiveCharacterTextSplitter applied
- Chunk size and overlap respected

**`test_embedder.py`**
- `embed_batch(["text"])` → returns list of floats (mocked)
- Batch size respected
- Empty list input → returns []

**`test_qdrant_ops.py`**
- upsert: correct payload fields set
- delete_by_file_path: correct filter used
- check_exists: returns True when point found, False otherwise
- search: returns scored results

**`test_traverser.py`**
- Excluded path skipped
- Excluded extension skipped
- Disabled extension skipped
- Already-indexed unchanged file → skipped
- Changed file (new modified_at) → not skipped

**`test_runner.py`**
- Stop flag: file in progress completes, next file not started
- Rollback: incomplete file's Qdrant points deleted on stop
- Resume: pending files from the immediately previous stopped run processed first
- Completed run after a stopped run does not replay stale pending files

---

### Router tests

**`test_routers/test_index.py`**
- POST /api/index/start with session → 200, run created
- POST /api/index/start with API key → 200
- POST /api/index/start with no auth → 401
- POST /api/index/start when already running → 409
- POST /api/index/stop when not running → 400

**`test_routers/test_search.py`**
- GET /api/search?q=computer → 200, results grouped by file
- Filter by department → only matching files returned
- Pagination → correct page slice
- Empty query → 400

**`test_routers/test_config.py`**
- CRUD for folders, exclusions, file_types, departments, doc_types, synonyms
- Invalid extension format → 422
- Duplicate extension → 409

**`test_routers/test_incremental.py`**
- POST /api/incremental/preview → returns path list without deleting
- Invalid XML path → 400

---

### Integration notes

- Embedding calls are always mocked in tests — no model downloaded during CI
- Qdrant is fully mocked — no Qdrant instance needed for tests
- File system access is mocked using `tmp_path` (pytest fixture)

---

## 20. Build Order & Implementation Status

### Completed Implementation Checklist (35/35 Steps Done)

- [x] **Step 1:** `app/database.py`, `app/models.py` — Schema, engine, session factory
- [x] **Step 2:** `app/config.py` — Config loader, default values seeder, memory caching
- [x] **Step 3:** `app/logger.py` — Structured logger, rotating file handler, SSE log stream queue
- [x] **Step 4:** `app/auth.py` + `app/routers/auth.py` — Session cookie, API key authentication, login/logout routes
- [x] **Step 5:** `app/main.py` — FastAPI initialization, router registration, lifespan startup seeding
- [x] **Step 6:** `app/templates/base.html` + `login.html` — Base layout and login page
- [x] **Step 7:** `app/routers/config.py` — System settings, folders, exclusions, file types, departments, doc types, synonyms CRUD
- [x] **Step 8:** `app/templates/` — `folders.html`, `exclusions.html`, `file_types.html`, `departments.html`, `doctypes.html`, `synonyms.html`, `settings.html`
- [x] **Step 9:** `app/indexer/chunker/base.py` + `registry.py` — `ChunkResult` dataclass, `BaseChunker` ABC, registry map
- [x] **Step 10:** `app/indexer/chunker/excel.py` — `ExcelChunker` sheet-aware row-grouping
- [x] **Step 11:** `app/indexer/chunker/heading.py` — `HeadingAwareChunker` for DOCX, MD, TXT
- [x] **Step 12:** `app/indexer/chunker/slide.py` — `SlideChunker` for PPTX slide split & notes
- [x] **Step 13:** `app/indexer/chunker/generic.py` — `GenericChunker` for PDF, HTML, fallback
- [x] **Step 14:** `app/indexer/converter.py` — `DocumentConverter` wrapping MarkItDown
- [x] **Step 15:** `app/indexer/embedder.py` — `Embedder` wrapping SentenceTransformers
- [x] **Step 16:** `app/indexer/qdrant_ops.py` — Qdrant setup, scroll, delete, upsert, vector search, payload update
- [x] **Step 17:** `app/indexer/classifier.py` — Department and DocType glob pattern matching
- [x] **Step 18:** `app/indexer/xml_parser.py` — Incremental XML parser and backup path converter (`PC135(D.)` -> UNC)
- [x] **Step 19:** `app/indexer/traverser.py` — Folder walking, path/extension exclusions, skip unchanged logic
- [x] **Step 20:** `app/indexer/runner.py` — `IndexerRunner` thread pool orchestrator, rollback on stop signal
- [x] **Step 21:** `app/routers/index.py` — Start, stop, status, and run history endpoints
- [x] **Step 22:** `app/templates/dashboard.html` — Live progress, status badge, counters, start/stop controls
- [x] **Step 23:** `app/templates/incremental.html` — Incremental XML path inputs & preview table
- [x] **Step 24:** `app/routers/incremental.py` — Saved XML config and preview endpoints
- [x] **Step 25:** `app/search/synonyms.py` — Synonym query expansion logic
- [x] **Step 26:** `app/search/engine.py` — `SearchEngine` vector search, file scoring, exact phrase boost & highlighting
- [x] **Step 27:** `app/routers/search.py` — Public search API endpoint
- [x] **Step 28:** `app/routers/reclassify.py` — Reclassify endpoint without re-embedding
- [x] **Step 29:** `app/templates/logs.html` — Real-time SSE log tail viewer & history downloader
- [x] **Step 30:** `app/routers/config.py` (Logs) — Log history and SSE streaming endpoints
- [x] **Step 31:** `tests/conftest.py` — In-memory SQLite, Qdrant/Embedder mocks, TestClient fixtures
- [x] **Step 32:** `tests/test_indexer/` — Unit tests for xml_parser, classifier, chunkers, converter, embedder, qdrant_ops, traverser, runner
- [x] **Step 33:** `tests/test_routers/` & `tests/test_search/` — Unit & integration tests for auth, search, index, config, incremental, reclassify, synonyms
- [x] **Step 34:** `static/css/app.css` — CSS design system, dark sidebar, glassmorphism, responsive tables, badge colors
- [x] **Step 35:** `static/js/app.js` — Dashboard polling, form AJAX handlers, SSE log stream, API key copy

---

### Verification and Compatibility Fixes (2026-10-03)

- Added the missing `Any` typing import in `app/logger.py`, which previously prevented pytest collection.
- Updated template rendering in `app/main.py` to use the current Starlette `TemplateResponse` calling convention.
- Added `pytest.ini` with `--import-mode=importlib` to support the existing `tests/test_search.py` module alongside the `tests/test_search/` package.
- Updated the test SQLite fixture to use a shared in-memory connection so FastAPI request-thread tests see the initialized schema.
- Corrected test setup for the seeded synonym term and form-login redirect behavior.
- Renamed the visible product to **DocSearch indexer** across the application metadata, page titles, branding, and login screen.
- Replaced UI emojis with a consistent inline SVG icon sprite and accessible decorative icon markup; no external icon dependency was added.
- Added inline Edit/Save/Cancel controls for Department and Doc Type classification rules, with duplicate-name validation on updates and regression coverage.
- Improved Excel preprocessing to normalize `NaN`, `None`, `null`, `NaT`, and `Unnamed: N` conversion artifacts before the cleaned text is both embedded and stored in search payloads.
- Verified the converted `Messy_WebView_Research.xlsx` output: 222 chunks produced with zero `NaN`, `Unnamed:`, or `None` artifacts.
- Direct conversion verification of `SampleFolders/04_office/Messy_WebView_Research.xlsx` also produced 222 clean chunks with zero `NaN`, `Unnamed:`, or `None` artifacts.
- Existing Qdrant payloads require a re-index after this preprocessing change; the live app was unavailable on port 8000 during verification.
- Added a thread-safe `Embedder` cache keyed by model name and dimensions so search requests reuse the loaded SentenceTransformer model instead of loading it per request.
- Extended incremental XML path handling to preserve direct local and UNC paths, normalize forward slashes, and continue converting legacy `PC135(D.)` backup paths. Incremental processing now accepts only `FILE` entries; `FOLDER` entries are ignored.
- Fixed resume behavior so a completed run cannot replay stale pending files from an older stopped run; duplicate per-run skipped records are also prevented.
- Validation completed successfully:
  - `python -m pytest -q` → **40 passed** (11 non-blocking dependency deprecation warnings)
  - `python -m compileall -q app tests` → passed
  - Uvicorn smoke test → `/login` 200, `/docs` 200, unauthenticated `/api/index/status` 401
- No package dependencies were added or changed; `requirements.txt` remains unchanged.

---

### What is Left to Finish
**Nothing! All 35 steps outlined in the build plan are 100% complete and fully implemented.**

---

## 21. Requirements

```txt
# requirements.txt

# Web framework
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
jinja2>=3.1.4
python-multipart>=0.0.9
itsdangerous>=2.2.0
starlette>=0.37.2

# Database
sqlalchemy>=2.0.30

# Auth
bcrypt>=4.1.3
passlib[bcrypt]>=1.7.4

# Vector DB
qdrant-client>=1.9.0

# Embeddings
sentence-transformers>=3.0.0
torch>=2.3.0          # CPU version sufficient: torch --index-url https://download.pytorch.org/whl/cpu

# File conversion
markitdown>=0.0.1a2

# Chunking
langchain-text-splitters>=0.2.0

# Utilities
python-dotenv>=1.0.1

# Testing
pytest>=8.2.0
pytest-mock>=3.14.0
httpx>=0.27.0         # required by TestClient
pytest-asyncio>=0.23.0
```

> **Note on torch:** Install CPU-only torch to avoid 2GB GPU download:
> `pip install torch --index-url https://download.pytorch.org/whl/cpu`

---

*End of build plan.*
