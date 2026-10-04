# Folder Deletion Safety and Standalone DocSearch Demo Plan

> **Status:** Proposed  
> **Date:** 2026-10-04  
> **Scope:** Safe configured-folder deletion and an independent search demo page

## 1. Goals

Implement both requirements without changing the existing indexing/search contract:

1. When an administrator deletes a configured index folder:
   - Require a server-generated random six-digit confirmation code.
   - Delete the folder's SQLite configuration row.
   - Delete every Qdrant point whose normalized `file_path` is the folder itself or a descendant.
   - Never delete a sibling path such as `C:\docs-archive` when deleting `C:\docs`.
   - Preserve compatibility with older Qdrant server/client versions.
   - Surface Qdrant failures instead of reporting a successful database-only deletion.

2. Add an independent `DocSearch.html` page:
   - Fetch the existing `/api/search` endpoint.
   - Expose every search, filter, and pagination parameter currently supported by the endpoint.
   - Render ranked file results, scores, metadata, excerpts, synonym information, loading, empty, and error states.
   - Work without the Jinja admin layout or the admin JavaScript bundle.

## 2. Current Repository Baseline

The implementation should extend the existing seams rather than create a second indexing/search path.

- [`app/routers/config.py`](app/routers/config.py) currently implements
  `DELETE /api/config/folders/{folder_id}`, but it only deletes the
  [`IndexFolder`](app/models.py) row.
- [`app/indexer/qdrant_ops.py`](app/indexer/qdrant_ops.py) already:
  - normalizes Windows paths before storing them;
  - creates a `KEYWORD` payload index for `file_path`;
  - deletes all points for one exact file path using `MatchValue`;
  - supports older client signatures through narrow `TypeError` fallbacks.
- [`app/indexer/paths.py`](app/indexer/paths.py) provides
  `normalize_file_path`, `canonical_file_path`, and `path_is_within`.
- The current search API is [`app/routers/search.py`](app/routers/search.py):
  `GET /api/search?q=...&department=...&doc_type=...&extension=...&page=...&per_page=...&exact=...`.
- [`app/search/engine.py`](app/search/engine.py) groups vector hits by file and
  returns `results`, `total_files`, `total_pages`, `page`, `per_page`, `query`,
  `synonyms_used`, and `exact_mode`.
- [`app/main.py`](app/main.py) serves the application and mounts `/static`.
- Existing router and Qdrant tests are in
  [`tests/test_routers/test_config.py`](tests/test_routers/test_config.py) and
  [`tests/test_indexer/test_qdrant_ops.py`](tests/test_indexer/test_qdrant_ops.py).

## 3. Deletion Design

### 3.1 Folder membership and path safety

Use the shared path helpers for every comparison:

1. Normalize the configured folder path with `normalize_file_path`.
2. Compare paths case-insensitively for Windows paths using
   `canonical_file_path`.
3. Treat a point as belonging to the folder when
   `path_is_within(point_file_path, folder_path)` is true.
4. Include a file whose path is exactly the configured folder only for
   completeness; normal files will normally be descendants.
5. Enforce a separator-aware boundary so `C:\docs2` is not considered inside
   `C:\docs`.
6. Keep the path comparison independent of the host operating system because
   the application indexes Windows and UNC paths.

### 3.2 Qdrant compatibility strategy

Do not send a wildcard string to `MatchValue`. Older Qdrant versions treat
`MatchValue` as an exact keyword match, not as a glob or prefix expression.

Implement a dedicated helper, for example
`delete_points_under_path(client, collection_name, folder_path, ...)`, with
the following compatibility-first behavior:

1. Ensure the collection has a `KEYWORD` payload index for `file_path`.
   Existing points already contain the normalized field; indexing must remain
   idempotent for both new and existing collections.
2. Scroll through the collection in bounded pages, requesting point IDs and
   the `file_path` payload only. Use the existing `file_path` index where the
   installed/server version supports a compatible filter.
3. Apply the normalized, separator-aware `path_is_within` check to each
   returned payload. This is the correctness path for older Qdrant versions
   and avoids relying on version-specific wildcard or text-match semantics.
4. Delete matched point IDs in bounded batches using the oldest supported
   point-ID selector available in the client. Keep the existing narrow
   fallbacks for clients that reject `timeout` or `wait`; do not use a broad
   catch that converts a failed deletion into success.
5. Continue until every scroll page is processed. Do not stop after the
   first 500 points; a large document/folder can have many chunks.
6. Return a structured result such as `matched_points`, `deleted_points`, and
   `batches`, and raise a typed/explicit error when Qdrant cannot complete the
   operation.

An optional server-side text/prefix filter may be added as an optimization
when its capability is positively detected, but it must not replace the
scroll-and-boundary-check fallback. The fallback must work with the older
Qdrant versions that the application claims to support.

### 3.3 Confirmation challenge

Use a two-step, server-enforced challenge so the safety check is not only a
client-side prompt:

1. Add `POST /api/config/folders/{folder_id}/delete-challenge`.
   - Require the existing session authentication.
   - Verify that the folder exists.
   - Generate a six-digit code with `secrets.randbelow`, constrained to
     `100000..999999` so leading-zero ambiguity is avoided.
   - Persist only a hash of the code, the folder ID, creation/expiry time,
     authenticated session/user binding, and a consumed timestamp.
   - Return a challenge ID, the six-digit code to display to the administrator,
     and a short expiry (for example, ten minutes).
2. Add a request model for the destructive operation, containing the
   challenge ID and the code typed by the administrator.
3. Change `DELETE /api/config/folders/{folder_id}` to require that request.
   - Reject missing, malformed, expired, wrong, already-consumed, or
     folder-mismatched challenges with a clear `400`/`409` response.
   - Compare the submitted code against the stored hash.
   - Consume the challenge exactly once after successful validation.
4. Do not expose a destructive delete path that accepts only the folder ID.

The six-digit code is an accidental-deletion guard, not an authorization
mechanism. The existing session/API authentication remains required.

### 3.4 Deletion transaction and failure behavior

The endpoint must coordinate Qdrant and SQLite in a safe order:

1. Reject deletion with `404` if the folder no longer exists.
2. Reject with `409` while an indexing run is active, or otherwise coordinate
   with the runner so the runner cannot re-index the folder after deletion.
   The first implementation should use the explicit `409` gate and tell the
   user to stop the active run.
3. Validate and consume the challenge under the existing SQLite write
   coordination.
4. Delete all matching Qdrant points and wait for completion.
5. Only after Qdrant succeeds, delete the `IndexFolder` row and commit.
6. If Qdrant fails or times out:
   - keep the folder row;
   - return an error such as `502`/`503` with an actionable message;
   - log the folder path, folder ID, collection, and failure;
   - do not claim that deletion completed.
7. If the folder has no matching points, treat the Qdrant operation as a
   successful no-op and remove the configuration row.
8. Return a response containing the folder ID/path and deletion counts so the
   UI can report what happened.

If a failure occurs after some point-ID batches have already been deleted,
report the operation as failed/partial and retain the folder row for retry.
The plan does not promise rollback of remote Qdrant deletes; the implementation
must make retries idempotent.

### 3.5 Indexing and incremental-delete consistency

- Keep `file_path` in every newly indexed payload and keep
  `ensure_collection` responsible for the payload index.
- Verify that reindexing, incremental XML deletion, reclassification, and
  folder deletion all use the same normalization helper.
- Do not remove the existing exact-file deletion helper; use the new
  folder-prefix helper only for configured-folder deletion.
- Ensure a folder deletion cannot be followed by the current indexing run
  rediscovering and re-indexing the same files.

## 4. Standalone `DocSearch.html` Design

### 4.1 Location and serving

Create [`static/DocSearch.html`](static/DocSearch.html) as a self-contained
HTML document with inline CSS and JavaScript. Add a direct application route
`/DocSearch.html` in [`app/main.py`](app/main.py) that serves this file, while
retaining `/static/DocSearch.html` as the static asset path if useful.

The page must not extend `base.html`, depend on `app.js`, or require a
frontend build. The normal supported usage is through the running FastAPI
application; opening the file directly as `file://` is not required because
browser CORS rules can prevent the fetch.

### 4.2 Search controls

Build the query using `URLSearchParams` and append repeated parameters for
multi-value filters:

- required free-text query `q`;
- exact phrase checkbox `exact`;
- one or more department values `department`;
- one or more document type values `doc_type`;
- one or more file extensions `extension`;
- page number `page`;
- page size `per_page`, bounded to the API's accepted range `1..100`.

Use free-form comma-separated filter inputs or repeatable filter chips so the
standalone page does not need authenticated admin configuration endpoints just
to render. Trim blank values and preserve the values in the request.

Add a configurable endpoint base URL and optional `X-API-Key` input only if
the page is expected to call a different origin or a deployment later protects
the search route. Same-origin search should work with an empty base URL and no
extra header.

### 4.3 Results and pagination

Render the response contract from `SearchEngine`:

- file name and normalized path;
- score;
- file extension;
- department and document-type labels;
- every returned excerpt's section context, chunk index, and highlighted text;
- query, exact mode, synonyms used, total files, and total pages.

Implement first/previous/next/last controls, a page number display, page-size
selection, and disabled states at the boundaries. Reset to page 1 whenever
the query or a filter changes. Preserve the current query in the URL with
`history.replaceState` so a search can be refreshed or shared.

Render all server-provided values safely. Excerpt highlighting currently uses
`<mark>` tags, so allow only that intended tag or render excerpts through a
small sanitizer; escape file paths, labels, and all other text before inserting
it into the DOM.

Provide explicit loading, empty-result, invalid-query, network/API-error, and
unauthorized states. Do not silently show an empty result when the request
failed.

## 5. Files and Symbols to Change

### Backend

- [`app/models.py`](app/models.py)
  - Add a short-lived folder-delete challenge model, or an equivalent
    persisted challenge representation.
- [`app/database.py`](app/database.py)
  - Add an additive/idempotent schema path for challenge storage if the
    existing startup migration pattern requires it.
- [`app/indexer/qdrant_ops.py`](app/indexer/qdrant_ops.py)
  - Add bounded descendant-path discovery and point-ID deletion helpers.
  - Preserve exact-file deletion and older-client fallbacks.
- [`app/routers/config.py`](app/routers/config.py)
  - Add the challenge endpoint and request model.
  - Change folder deletion to validate the challenge and coordinate Qdrant
    before committing SQLite.
- [`app/main.py`](app/main.py)
  - Serve `/DocSearch.html`.

### Frontend

- [`static/DocSearch.html`](static/DocSearch.html)
  - Add the independent search UI, inline styling, fetch layer, rendering,
    filter serialization, pagination, URL state, and error handling.
- [`static/js/app.js`](static/js/app.js)
  - Update the existing folder delete flow to request/display the challenge,
    collect the typed six-digit code, submit the challenge, and refresh only
    after successful deletion.
- [`app/templates/folders.html`](app/templates/folders.html)
  - Add any modal/dialog markup needed by the existing admin page, unless the
    challenge dialog is created entirely by the existing JavaScript pattern.

### Tests

- [`tests/test_indexer/test_qdrant_ops.py`](tests/test_indexer/test_qdrant_ops.py)
- [`tests/test_routers/test_config.py`](tests/test_routers/test_config.py)
- Add a focused page/route test near the existing router tests, for example
  `tests/test_docsearch_page.py`.
- Extend search tests only where the standalone page requires a clarified API
  contract; do not duplicate the search engine implementation in the demo.

## 6. Test Plan

### Qdrant operation tests

Cover:

- exact folder-root match;
- descendant matches with both slash styles;
- Windows case-insensitivity;
- separator boundary (`C:\docs` matches `C:\docs\file.txt` but not
  `C:\docs2\file.txt`);
- UNC paths;
- multiple scroll pages and more than 500 points;
- bounded point-ID delete batches;
- no deletion for points outside the folder;
- empty collection/no-op deletion;
- old-client signatures that reject `timeout` or `wait`;
- Qdrant errors being raised/reported rather than converted to success;
- preservation of the normalized `file_path` payload index.

### Folder endpoint tests

Cover:

- challenge creation returns exactly six decimal digits and an expiry;
- missing, non-numeric, wrong-length, wrong, expired, consumed, and
  folder-mismatched codes are rejected;
- the wrong code leaves both SQLite and Qdrant unchanged;
- an active index run returns `409`;
- a successful delete removes all matching points and then the folder row;
- a Qdrant failure keeps the folder row and returns an error;
- a folder with no Qdrant points is removed as a successful no-op;
- replaying a successful challenge is rejected;
- unrelated folders/points remain intact.

### Standalone page tests

At minimum:

- `GET /DocSearch.html` returns `200` and contains the independent page;
- the page contains controls for all current search parameters;
- repeated filter parameters are serialized correctly;
- page changes preserve filters and query;
- empty, error, and result states have visible rendering paths;
- file paths and metadata are escaped while intended excerpt highlighting works.

Use browser-level tests if the repository later adopts a browser test runner;
otherwise keep the HTML/JavaScript logic small enough for focused static and
endpoint contract tests.

## 7. Implementation Order

1. Add the challenge storage model/migration and request/response contract.
2. Implement and unit-test normalized descendant matching and bounded Qdrant
   point-ID deletion, including legacy-client fallbacks.
3. Add the challenge endpoint and replace the folder delete endpoint with the
   Qdrant-first, SQLite-second flow.
4. Add active-run protection, structured logging, explicit errors, and
   response counts.
5. Update the existing folders UI with the challenge display/input flow.
6. Add and serve `static/DocSearch.html`.
7. Add focused tests, run the targeted Qdrant/router/page suites, then run the
   full existing test suite if targeted tests pass.
8. Update the relevant API/build documentation if endpoint details change.

## 8. Acceptance Criteria

- Clicking Delete never removes a folder without a correctly typed,
  unexpired, server-issued six-digit code.
- A successful folder deletion removes every vector for that folder and its
  descendants, including all chunks, while preserving sibling and unrelated
  paths.
- The implementation does not rely on wildcard behavior unsupported by older
  Qdrant versions; `file_path` remains indexed and the compatibility fallback
  performs an exhaustive, bounded, separator-aware match.
- Qdrant failure is visible to the administrator and does not result in a
  database-only success response.
- A successful deletion is idempotently retryable after partial remote
  progress.
- `DocSearch.html` is independently served, has no admin-template dependency,
  fetches `/api/search`, exposes all current filters and exact mode, and
  supports page navigation and page-size changes.
- Search results, highlighted excerpts, metadata, empty states, loading states,
  and errors are rendered safely and clearly.
- Existing indexing, incremental deletion, reclassification, search behavior,
  authentication, and unrelated configuration CRUD remain passing.

