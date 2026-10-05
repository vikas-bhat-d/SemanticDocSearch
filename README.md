# SemanticDocSearch

SemanticDocSearch is a local semantic document indexer and search service. It
converts supported files to Markdown with MarkItDown, splits the converted
content into searchable chunks, creates local SentenceTransformers embeddings,
and stores vectors plus metadata in Qdrant. A FastAPI application provides an
admin UI, indexing controls, incremental XML processing, live logs, and a
search API.

The application is designed for local files and Windows local/UNC paths, but
the Python code can also run on other operating systems when the configured
paths are accessible to the process.

## Contents

- [SemanticDocSearch](#semanticdocsearch)
  - [Contents](#contents)
  - [Architecture](#architecture)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Start Qdrant](#start-qdrant)
  - [Configure and start the application](#configure-and-start-the-application)
    - [First-time credentials and API key](#first-time-credentials-and-api-key)
  - [First-time setup](#first-time-setup)
  - [Configure the indexer](#configure-the-indexer)
    - [Default file types and chunkers](#default-file-types-and-chunkers)
    - [Exclusions](#exclusions)
    - [Department and document-type classification](#department-and-document-type-classification)
    - [Synonyms](#synonyms)
    - [Settings and defaults](#settings-and-defaults)
  - [Run a full index](#run-a-full-index)
  - [Run an incremental XML index](#run-an-incremental-xml-index)
  - [Search indexed documents](#search-indexed-documents)
    - [Standalone search page](#standalone-search-page)
    - [Search API](#search-api)
  - [HTTP API quick reference](#http-api-quick-reference)
  - [Data, logs, and backups](#data-logs-and-backups)
  - [Testing](#testing)
  - [Troubleshooting](#troubleshooting)
    - [`Connection refused` or Qdrant errors](#connection-refused-or-qdrant-errors)
    - [The model fails to load or the first run appears stalled](#the-model-fails-to-load-or-the-first-run-appears-stalled)
    - [A file is skipped](#a-file-is-skipped)
    - [Changed content does not appear in search](#changed-content-does-not-appear-in-search)
    - [A normal run finds zero files after a successful run](#a-normal-run-finds-zero-files-after-a-successful-run)
    - [Search results are empty](#search-results-are-empty)
    - [`401 Unauthorized`](#401-unauthorized)
    - [UNC paths cannot be read](#unc-paths-cannot-be-read)
  - [Repository layout](#repository-layout)

## Architecture

The indexing pipeline is:

```text
Configured folders or incremental XML
              |
              v
Filesystem discovery and exclusion rules
              |
              v
MarkItDown conversion to Markdown
              |
              v
File-type-aware chunking
              |
              v
Local SentenceTransformers embeddings
              |
              v
Qdrant collection (vectors and searchable metadata)
```

SQLite stores application configuration, authentication hashes, configured
folders and rules, incremental XML paths, and index-run history. Qdrant is the
source of truth for indexed document chunks; file contents are not stored in
SQLite.

The indexer runs in the FastAPI process. A bounded producer/worker pipeline
discovers files, converts them, embeds chunks, and upserts bounded batches to
Qdrant. It does not require a separate worker service.

## Prerequisites

Install the following before starting the application:

1. **Python**: Python 3.10 or newer is recommended. The repository does not
   declare a strict Python floor, so use a version for which the dependency
   wheels in `requirements.txt` are available.
2. **Qdrant**: a running Qdrant instance reachable over its HTTP REST API.
   The default address is `localhost:6333`.
3. **Source access**: the account running Python must be able to read every
   local or UNC folder that you configure.
4. **Network access on first use**: SentenceTransformers normally downloads
   `sentence-transformers/all-MiniLM-L6-v2` the first time it is loaded.
   Pre-cache the model or configure a local model path for an offline
   deployment.
5. **Docker Desktop** is optional, but is the simplest way to run Qdrant on
   Windows.

## Installation

Install the dependencies into the active system Python installation. The
following commands are for Windows PowerShell:

```powershell
cd C:\vikas\BE\Projects\SemanticDocSearcher
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` contains both application and test dependencies:

| Area | Packages |
| --- | --- |
| Web application | `fastapi`, `uvicorn[standard]`, `jinja2`, `python-multipart`, `itsdangerous`, `starlette` |
| Persistence and authentication | `sqlalchemy`, `bcrypt`, `passlib[bcrypt]` |
| Indexing and search | `qdrant-client`, `sentence-transformers`, `torch`, `markitdown`, `langchain-text-splitters` |
| Configuration and tests | `python-dotenv`, `pytest`, `pytest-mock`, `httpx`, `pytest-asyncio` |

There is no separate `package.json` or frontend build step. The admin UI is
served directly by FastAPI from the `app/templates` and `static` directories.

## Start Qdrant

Run Qdrant separately from the Python application. For a quick local Docker
deployment:

```powershell
docker volume create semanticdocsearch-qdrant
docker run --name semanticdocsearch-qdrant `
  -p 6333:6333 -p 6334:6334 `
  -v semanticdocsearch-qdrant:/qdrant/storage `
  qdrant/qdrant
```

Verify that it is reachable before starting the application:

```powershell
curl.exe http://localhost:6333/collections
```

The application uses Qdrant's HTTP client on the configured host and port. It
automatically creates the configured collection on the first index run and
creates keyword payload indexes used for filtering, skip checks, and folder
cleanup. The default collection is `knowledge_base`.

If Qdrant runs elsewhere, change `qdrant_host` and `qdrant_port` on the
Settings page before starting an index run. Qdrant authentication and TLS are
not configured by this application; put Qdrant behind an appropriate protected
network boundary if it is not local.

## Configure and start the application

The application creates these directories and files automatically:

- `data/config.db` - SQLite configuration and run history database.
- `logs/app.log` - rotating application log.


```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For local development, automatic reload is convenient:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open <http://127.0.0.1:8000/login> after the server starts.

Configuration is stored in SQLite. Although `python-dotenv` is installed, the
current application does not automatically load a `.env` file. Set
environment variables in the process or configure application settings in the
admin UI.

### First-time credentials and API key

On an empty database, startup seeds:

- Admin username: `admin`
- Admin password: `admin`
- A random API key beginning with `sk-`

Log in immediately and change the admin password from **Settings**. The
initial API key is exposed through the Settings page while it is available in
the running process. Copy it before restarting if you intend to automate
indexing. If it is lost, use **Regenerate API Key** in Settings and store the
returned key securely. Do not commit API keys, `data/config.db`, or session
secrets to source control.

## First-time setup

Use this order for a new installation:

1. Start Qdrant.
2. Start SemanticDocSearch and open `/login`.
3. Sign in with the initial admin credentials and change the password.
4. Open **Settings** and confirm the Qdrant host, port, collection name,
   embedding model, and embedding dimensions.
5. Open **Index Folders** and add one or more absolute local or UNC paths.
6. Review **File Types** and **Exclusions**.
7. Optionally add department rules, document-type rules, and synonyms.
8. Start indexing from the dashboard.
9. Open `/DocSearch.html` or call the search API after the run completes.

The admin pages are:

| URL | Purpose |
| --- | --- |
| `/` | Dashboard, start/stop controls, progress, and recent runs |
| `/folders` | Add or delete configured index folders |
| `/file-types` | Map extensions to chunkers and enable/disable them |
| `/exclusions` | Exclude path prefixes/globs or extensions |
| `/departments` | Classify files using case-insensitive path patterns |
| `/doc-types` | Classify files using document-type path patterns |
| `/synonyms` | Manage semantic query expansion terms |
| `/incremental` | Save and preview changed/deleted XML inputs |
| `/settings` | Embedding, Qdrant, worker, chunking, search, limits, and security settings |
| `/logs` | Historical and live application logs |
| `/DocSearch.html` | Standalone search page (public by default) |

All admin UI pages except `/login` require the authenticated session cookie.
The standalone `/DocSearch.html` page and `GET /api/search` are public by
default.

## Configure the indexer

### Default file types and chunkers

The default file-type mappings are:

| Extensions | Chunker | Behavior |
| --- | --- | --- |
| `.xlsx`, `.xls`, `.csv` | `excel` | Keeps sheet context and groups table rows |
| `.docx`, `.doc`, `.md`, `.txt` | `heading` | Preserves Markdown headings and section context |
| `.pptx`, `.ppt` | `slide` | Preserves slide numbers and splits long slides |
| `.pdf`, `.html`, `.htm` | `generic` | Uses word-based chunks with overlap |

MarkItDown performs conversion before chunking. A file must be both supported
by MarkItDown and enabled in **File Types**. Other extensions are skipped by
default, including common structured or media formats in the sample corpus.
You can add an extension in the UI and select one of `excel`, `heading`,
`slide`, or `generic`, but the selected converter must produce content in a
format that the chunker understands.

Changing a mapping affects future indexing. It does not rewrite points already
stored in Qdrant; use an incremental changed-file entry or remove/recreate the
folder when a complete rebuild is required.

### Exclusions

Add either:

- a **path** value, which matches a case-insensitive path prefix or `fnmatch`
  glob; or
- an **extension** value such as `.tmp` or `tmp`, which is normalized to a
  leading dot and compared case-insensitively.

Exclusions apply during normal discovery and incremental-file processing.
Adding an exclusion does not delete points that were already indexed.

### Department and document-type classification

Each rule has a name and one or more path patterns. Patterns are matched
case-insensitively after `/` is normalized to `\`, using Python `fnmatch`
semantics. Examples:

```text
Department: HR
Patterns:
*\HR\*
*\Human Resources\*

Document type: Policy
Patterns:
*\policy\*
*\policies\*
```

Classification is written into each Qdrant point at indexing time and is
available as a search filter. Editing a rule does not relabel existing points.
Reindex affected files, or call `POST /api/reclassify` for a single file to
update all of that file's Qdrant points.

### Synonyms

For non-exact semantic searches, a configured term is expanded with its
synonyms. The default dictionary includes terms such as `computer`,
`document`, `invoice`, and `employee`. Exact-mode searches do not expand
synonyms. The search response reports the synonyms that were used.

### Settings and defaults

Settings are persisted in SQLite and can be changed on the **Settings** page
or with `PUT /api/config/settings`. The most important defaults are:

| Setting | Default | Purpose |
| --- | ---: | --- |
| `embedding_model` | `sentence-transformers/all-MiniLM-L6-v2` | SentenceTransformers model name or local path |
| `embedding_dimensions` | `384` | Vector size; must match the model |
| `qdrant_host` / `qdrant_port` | `localhost` / `6333` | Qdrant address |
| `collection_name` | `knowledge_base` | Qdrant collection |
| `index_workers` | `4` | Concurrent file workers |
| `index_queue_capacity` | `64` | Maximum queued file items |
| `embedding_batch_size` | `32` | Chunks sent to the embedder at once |
| `embedding_concurrency` | `1` | Concurrent embedding calls |
| `qdrant_upsert_batch_size` | `64` | Maximum points per Qdrant request |
| `qdrant_upsert_max_bytes` | `4194304` | Maximum serialized Qdrant request size |
| `chunk_size` / `chunk_overlap` | `512` / `64` | Generic and heading chunk word limits |
| `rows_per_chunk` | `15` | Excel data rows per chunk |
| `search_top_k` | `50` | Maximum chunks retrieved before grouping by file |
| `search_per_page` | `10` | Default search result page size |
| `search_excerpt_count` | `3` | Excerpts returned per file |
| `max_file_size_mb` | `100` | Maximum source file size |
| `max_markdown_chars` | `10000000` | Maximum converted Markdown size |
| `max_chunk_chars` | `200000` | Maximum individual chunk size |
| `conversion_timeout_seconds` | `300` | MarkItDown conversion timeout |
| `qdrant_timeout_seconds` | `30` | Qdrant operation timeout |
| `log_level` | `INFO` | `DEBUG`, `INFO`, `WARNING`, or `ERROR` logging threshold |

`parallel_workers` is retained as a compatibility alias for
`index_workers`. If both are supplied, the explicit `index_workers` value is
used.

Set the embedding model and dimensions before the first run. If the model or
dimension changes after a collection has been created, use a new
`collection_name` and perform a complete rebuild; Qdrant collections cannot
hold vectors with a different size.

## Run a full index

From the dashboard, click **Start Indexing**. The run:

1. Ensures the configured Qdrant collection exists.
2. Reads changed and deleted XML paths, if configured.
3. Deletes old Qdrant points for changed paths and deleted paths.
4. Discovers eligible files from folders in `pending`, `failed`, or `stopped`
   state.
5. Converts, chunks, embeds, and upserts each file.
6. Reports indexed, skipped, failed, and deleted counts.

Click **Stop Indexing** to send a cooperative stop signal. The status changes
to `STOPPING` while in-progress work drains, then becomes `STOPPED`. A run can
also become `FAILED` if discovery, conversion, embedding, or Qdrant work
fails.

Important indexing behavior:

- A normal run skips a file when any Qdrant point already exists for its
  normalized path. The indexer does not compare modification times or file
  hashes.
- Changed XML entries force replacement indexing. Deleted XML entries are
  removed and are excluded from rediscovery during that run.
- A folder that completes successfully is marked `completed` and is not
  automatically walked by later normal runs. Use changed XML for routine
  updates. For a complete folder rebuild, delete the configured folder from
  **Index Folders** (which removes its Qdrant points) and add it again, or
  use a new collection.
- Per-file run details are intentionally bounded. Large runs may retain only
  a sample of file-level diagnostic rows; the run status reports when details
  are incomplete.

Deleting a configured folder is destructive. The UI requires a six-digit
confirmation challenge, removes matching Qdrant points, and only then removes
the SQLite folder configuration. Stop active indexing before attempting it.

## Run an incremental XML index

Incremental XML is useful when an upstream system provides changed and deleted
file lists. Open `/incremental`, enter the two XML paths, save them, and use
**Preview Affected Paths** to validate the files. Start the run from the
dashboard.

The parser accepts an XML file path or XML content in this shape:

```xml
<?xml version="1.0" encoding="utf-8"?>
<NewDataSet>
  <FILELIST>
    <Type>FILE</Type>
    <Value>C:\Documents\HR\leave-policy.docx</Value>
  </FILELIST>
</NewDataSet>
```

Rules for incremental input:

- Only `FILE` entries with a non-empty `Value` are processed. Folder entries
  and other types are ignored.
- Direct local paths, UNC paths, and legacy paths such as
  `PC135(D.)\Desktop\file.xlsx` are accepted. The legacy form is converted to
  `\\pc135\D\Desktop\file.xlsx`.
- Changed files must still exist and must have an enabled file-type mapping.
- Deleted files do not need to exist; their Qdrant points are removed.
- If a path appears in both XML files, deleted takes precedence and it is not
  reindexed during that run.
- Path exclusions, extension exclusions, classification rules, and configured
  chunkers still apply.

The same operation can be started through the API:

```json
{
  "changed_xml_path": "C:\\Data\\changed.xml",
  "deleted_xml_path": "C:\\Data\\deleted.xml"
}
```

Send that object to `POST /api/index/start`. If the fields are omitted, the
last paths saved in SQLite are used.

## Search indexed documents

### Standalone search page

Open <http://127.0.0.1:8000/DocSearch.html>. The page supports:

- semantic search;
- exact phrase mode;
- repeated department, document-type, and extension filters;
- configurable page size and pagination;
- ranked files with scores, classifications, section context, and highlighted
  excerpts.

The page is intentionally independent of the admin layout and can also be
served separately when its endpoint points at a compatible API.

### Search API

`GET /api/search` is currently available without authentication:

```powershell
curl.exe --get "http://127.0.0.1:8000/api/search" `
  --data-urlencode "q=computer security policy" `
  --data-urlencode "department=HR" `
  --data-urlencode "extension=.docx" `
  --data-urlencode "page=1" `
  --data-urlencode "per_page=10"
```

Supported query parameters:

| Parameter | Description |
| --- | --- |
| `q` | Required query text |
| `department` | Repeat for one or more department filters |
| `doc_type` | Repeat for one or more document-type filters |
| `extension` | Repeat for one or more extension filters |
| `page` | 1-based page number |
| `per_page` | Results per page, from 1 to 100 |
| `exact` | `true` for strict phrase filtering |

Quoted text, for example `"leave policy"`, also enables exact phrase
behavior. Normal semantic searches expand configured synonyms, embed the
expanded query, retrieve the top chunks from Qdrant, group them by file, and
return the best excerpts per file.

A successful response has this shape:

```json
{
  "results": [
    {
      "file_name": "leave-policy.docx",
      "file_path": "C:\\Documents\\HR\\leave-policy.docx",
      "file_extension": ".docx",
      "departments": ["HR"],
      "doc_types": ["Policy"],
      "score": 0.8421,
      "excerpts": [
        {
          "text": "... highlighted excerpt ...",
          "chunk_index": 0,
          "section_context": "Section: Leave Policy"
        }
      ]
    }
  ],
  "total_files": 1,
  "total_pages": 1,
  "page": 1,
  "per_page": 10,
  "query": "computer security policy",
  "synonyms_used": [],
  "exact_mode": false
}
```

## HTTP API quick reference

The browser UI uses the same endpoints listed below. JSON requests should use
`Content-Type: application/json`.

| Method and path | Authentication | Purpose |
| --- | --- | --- |
| `POST /api/auth/login` | None | Form or JSON login; establishes a session cookie |
| `POST /api/auth/logout` | Session | Clear the session |
| `POST /api/index/start` | Session or `X-API-Key` | Start one indexing run |
| `POST /api/index/stop` | Session or `X-API-Key` | Request a cooperative stop |
| `GET /api/index/status` | Session or `X-API-Key` | Current run status and counters |
| `GET /api/index/runs` | Session | Paginated run history |
| `GET /api/index/runs/{run_id}/files` | Session | Paginated per-file diagnostics |
| `GET /api/config/settings` | Session | Read settings |
| `PUT /api/config/settings` | Session | Update settings, change password, or regenerate API key |
| `/api/config/folders` | Session | List/add/delete configured folders and deletion challenges |
| `/api/config/file-types` | Session | List/create/update/delete extension mappings |
| `/api/config/exclusions` | Session | List/create/delete exclusions |
| `/api/config/departments` | Session | CRUD department path rules |
| `/api/config/doc-types` | Session | CRUD document-type path rules |
| `/api/config/synonyms` | Session | CRUD query synonym rules |
| `GET /api/incremental/config` | Session | Read saved XML paths |
| `POST /api/incremental/config` | Session | Save XML paths |
| `POST /api/incremental/preview` | Session | Parse and preview XML paths |
| `POST /api/reclassify` | Session | Update classifications for every point of one file |
| `GET /api/logs/history` | Session | Read recent log lines |
| `GET /api/logs/stream` | Session | Receive live logs as Server-Sent Events |
| `GET /api/search` | None by default | Semantic or exact document search |

The API key is passed as `X-API-Key`. It is accepted for the three index
control/status endpoints that use general API authentication. Configuration,
run-history, log, incremental, and reclassification endpoints require the
admin session cookie.

For an API-only session login, use a cookie jar:

```powershell
curl.exe -c cookies.txt `
  -H "Content-Type: application/json" `
  -d "{\"username\":\"admin\",\"password\":\"admin\"}" `
  http://127.0.0.1:8000/api/auth/login

curl.exe -b cookies.txt http://127.0.0.1:8000/api/index/status
```

For scheduler-style indexing with an API key:

```powershell
curl.exe -X POST `
  -H "X-API-Key: <your-api-key>" `
  http://127.0.0.1:8000/api/index/start
```

## Data, logs, and backups

| Location | Contents |
| --- | --- |
| `data/config.db` | Settings, auth hashes, folders, rules, incremental paths, and run history |
| `logs/app.log` | Application log; rotates at 10 MB and keeps five backups |
| Qdrant collection | Embeddings, converted chunk text, file metadata, and classifications |

Stop the application before copying `data/config.db` for a consistent SQLite
backup. Back up the Qdrant collection separately; copying SQLite does not back
up vectors. Do not expose or commit the database because it contains
authentication hashes and configuration data.

## Testing

The test suite uses mocked Qdrant and embedding clients where appropriate, so
you normally do not need a live Qdrant service to run it:

```powershell
python -m pytest
```

The suite covers authentication, routers, search, conversion, traversal,
chunkers, embedding behavior, Qdrant operations, XML parsing, classification,
and index-run behavior.

## Troubleshooting

### `Connection refused` or Qdrant errors

Confirm that Qdrant is running and that **Settings** points to the correct
host and port:

```powershell
curl.exe http://localhost:6333/collections
```

### The model fails to load or the first run appears stalled

The embedding model may be downloading or initializing. Check `logs/app.log`
and the terminal output. Ensure the process has network access, disk space,
and enough memory. For an offline deployment, pre-cache the model and set
`embedding_model` to its local path.

### A file is skipped

Check the dashboard run counters and `/logs`. Common causes are:

- the extension is disabled or has no File Types mapping;
- the path or extension is excluded;
- the file is empty or produces empty Markdown;
- the source exceeds `max_file_size_mb`, `max_markdown_chars`, or the
  conversion timeout;
- the normalized file path already has a Qdrant point.

### Changed content does not appear in search

Normal indexing is presence-based and does not detect file modification
timestamps or hashes. Put the path in `changed_paths.xml` and run an
incremental index, or remove/recreate the folder for a full rebuild.

### A normal run finds zero files after a successful run

Completed folders are intentionally not included in later normal scans. Use
incremental XML for changed paths, or delete and add the folder again for a
clean rebuild.

### Search results are empty

Confirm that the index run completed, the configured collection contains
points, the selected filters match the stored classifications/extensions, and
the search model/dimensions match the model used for indexing.

### `401 Unauthorized`

Log in through `/login` for browser requests. For API automation, use the
session cookie for admin endpoints or send `X-API-Key` for index
start/stop/status. The search endpoint is unauthenticated by default.

### UNC paths cannot be read

Run the application under an account that can access the share. A path that
works in an interactive Explorer session may fail when Uvicorn is started by a
different Windows account or service.

## Repository layout

```text
app/
  main.py                 FastAPI application and page routes
  config.py               Defaults and SQLite-backed settings
  database.py             SQLite engine and schema migration
  models.py               SQLAlchemy models
  auth.py                 Session and API-key authentication
  routers/                Auth, index, search, configuration, XML, and reclassify APIs
  indexer/                Traversal, conversion, chunking, embedding, XML, and Qdrant code
  search/                 Query expansion and result ranking
  templates/              Admin UI templates
static/                   CSS, admin JavaScript, and standalone search page
tests/                    Unit and API tests
SampleFolders/            Synthetic conversion/indexing fixtures
requirements.txt          Python dependencies
data/                     Runtime SQLite database (created automatically)
logs/                     Runtime rotating log files (created automatically)
```
