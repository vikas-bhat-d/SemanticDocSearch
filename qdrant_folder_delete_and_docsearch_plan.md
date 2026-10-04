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

Qdrant does **not** provide a portable, separator-aware wildcard, prefix, or
regular-expression condition for a `KEYWORD` payload. `MatchValue` is exact
equality. `MatchText`/a `TEXT` index is a full-text/token filter, not a
filesystem path-prefix operator, and its availability/configuration is not a
safe compatibility contract for older Qdrant deployments. Do not send a
string such as `C:\docs\*` or `C:\docs%` to `MatchValue`; it will not mean
"all descendants".

The primary design must therefore encode folder membership at indexing time
and delete by an exact indexed membership value. This keeps the destructive
operation inside Qdrant while preserving older-server compatibility.

1. Keep the existing normalized `file_path` payload and `KEYWORD` index for
   exact-file skip, reindex, incremental-delete, search metadata, and audit
   operations.
2. Add an `index_roots` payload field to every point. It is an array of all
   normalized configured `IndexFolder.path` values that contain the file,
   compared with the shared separator-aware `path_is_within` helper. This
   handles nested configured folders without duplicating vectors or relying on
   which de-duplicated root was used for the filesystem walk.
3. Create a `KEYWORD` payload index for `index_roots` in
   `ensure_collection`. Qdrant keyword matching applies to array elements, so
   one exact `MatchValue(value=<normalized folder>)` matches a point when that
   folder is one of its indexed roots.
4. Add `index_roots` to the traversal item and pass it through
   `iter_point_batches`/`build_point`. Incremental XML items must compute the
   same membership list from all configured folders.
5. Delete a configured folder with Qdrant's filter selector directly:

   ```json
   POST /collections/{collection_name}/points/delete?wait=true
   {
     "filter": {
       "must": [
         {
           "key": "index_roots",
           "match": { "value": "c:\\docs" }
         }
       ]
     }
   }
   ```

   The Python equivalent is:

   ```python
   client.delete(
       collection_name=collection_name,
       points_selector=models.FilterSelector(
           filter=models.Filter(must=[
               models.FieldCondition(
                   key="index_roots",
                   match=models.MatchValue(value=normalized_folder),
               )
           ])
       ),
       wait=True,
   )
   ```

   This uses the long-standing filter-delete shape rather than a newer
   full-text or wildcard feature. A single folder requires only
   `MatchValue`; do not require `MatchAny` (documented as newer than the
   basic match condition) for compatibility.
6. Wait for the delete operation to complete, return the Qdrant operation
   result, and treat an unsupported request or timeout as an explicit
   failure. Retain the existing narrow client fallbacks for `timeout` and
   `wait` keyword differences, but never convert a failed delete into success.

### 3.2.1 Existing-point migration and legacy fallback

Points written before `index_roots` exists will contain `file_path` but cannot
be selected by the new exact membership filter. Handle this explicitly:

1. On startup/collection setup, create the `index_roots` index idempotently.
2. Prefer a bounded backfill that scrolls old points, computes all matching
   configured roots from each normalized `file_path`, and uses `set_payload`
   in bounded point-ID batches to add `index_roots`. Preserve every existing
   payload field.
3. Until backfill is complete, a folder delete must detect/report that legacy
   points may exist. It may use a bounded scroll of `file_path` payloads,
   apply `path_is_within` locally, and delete only the resulting point IDs in
   bounded `PointIdsList` requests. This is a migration fallback, not the
   normal deletion query.
4. The fallback must scan every scroll page, not only the default first page,
   and must never treat a partial scan as a successful complete deletion.
5. Record whether the result used the direct `index_roots` filter or the
   legacy fallback in logs and the API response.

This is the only place where application-side path matching is required.
After all points have `index_roots`, folder deletion is a single
server-side Qdrant filter operation with an exact indexed value.

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
- Add and populate `index_roots` for every newly indexed point, and keep its
  `KEYWORD` payload index in `ensure_collection`.
- Verify that reindexing, incremental XML deletion, reclassification, and
  folder deletion all use the same normalization helper.
- Do not remove the existing exact-file deletion helper; use the new
  `index_roots` filter only for configured-folder deletion.
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
  - Add `index_roots` to point construction and collection indexes.
  - Add direct filter-based folder deletion and the bounded legacy migration
    fallback.
  - Preserve exact-file deletion and older-client fallbacks.
- [`app/indexer/traverser.py`](app/indexer/traverser.py)
  - Attach all configured containing roots to each file item, including
    incremental file items.
- [`app/indexer/runner.py`](app/indexer/runner.py)
  - Pass `index_roots` through the bounded point-writing pipeline.
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
- direct `FilterSelector` deletion by exact `index_roots` value;
- a point with multiple `index_roots` values;
- multiple scroll pages and more than 500 legacy points;
- bounded point-ID delete batches for the legacy fallback;
- no deletion for points outside the folder;
- empty collection/no-op deletion;
- old-client signatures that reject `timeout` or `wait`;
- creation of both `file_path` and `index_roots` `KEYWORD` indexes;
- legacy-point backfill preserving existing payload fields;
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
- New points contain both normalized `file_path` and exact `index_roots`
  membership metadata, with `KEYWORD` indexes for both fields.
- Normal deletion is a Qdrant-server-side `FilterSelector` delete on the
  indexed `index_roots` value; it does not rely on wildcard behavior,
  `MatchText`, or a newer text-index feature.
- Existing points without `index_roots` are backfilled or handled by an
  exhaustive, bounded, separator-aware legacy fallback before success is
  reported.
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

## 9. Verified Qdrant References

These references were checked on 2026-10-04:

- [Qdrant filtering](https://qdrant.tech/documentation/search/filtering/) —
  `MatchValue` is equality-based; filters can be composed with `must`, and
  keyword matching applies to supported keyword payload values/arrays.
- [Qdrant payload indexes](https://qdrant.tech/documentation/manage-data/indexing/) —
  create a `KEYWORD` index with
  `PUT /collections/{collection_name}/index`.
- [Qdrant delete-points API](https://api.qdrant.tech/api-reference/points/delete-points) —
  the delete body accepts either a point-ID list or a `FilterSelector`, with
  `wait` and `timeout` query parameters.
- [Qdrant payload types](https://qdrant.tech/documentation/manage-data/payload/) —
  keyword payloads may be scalar or arrays; array values are suitable for
  exact membership filtering.

The implementation should use the stable keyword/filter-delete contract above,
not assume that a Qdrant text index can perform a filesystem-safe prefix or
regular-expression match.
