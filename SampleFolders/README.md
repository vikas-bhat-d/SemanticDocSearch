# SampleFolders

This directory is a synthetic, deliberately uneven document corpus for exercising a MarkItDown conversion and semantic indexing pipeline.

The workbook in `04_office/Messy_WebView_Research.xlsx` is the main stress fixture. It contains 15 sheets with sparse cells, long prose, repeated headers, merged title cells, code snippets, URLs, dates, numeric logs, formulas, and far-apart values. `00_reference/Original_Messy_WebView_Research.xlsx` is the small workbook supplied with the request.

## Corpus layout

- `00_reference` contains the supplied small workbook and a short baseline note for comparing small and large conversion runs.
- `01_text` contains long Markdown, plain text, and a log-like file with repeated and multiline content.
- `02_structured` contains large CSV, TSV, JSON, and XML files.
- `03_web` contains an HTML capture with headings, tables, lists, code, comments, and irregular whitespace.
- `04_office` contains XLSX, DOCX, PPTX, and PDF files.
- `05_media` contains a small SVG and a text-heavy SVG variant for optional image/plugin tests.
- `06_edge_cases` contains an empty file, whitespace-only content, a duplicate, a Unicode file, and an unsupported binary fixture.
- `07_incremental` contains changed and deleted XML path lists using Windows-style paths.
- `08_metadata` contains a manifest and suggested search queries.

## Suggested checks

1. Convert every file and record success, skipped, and failed statuses.
2. Confirm that each Excel sheet name appears before its converted content.
3. Confirm that blank rows do not create long runs of empty Markdown.
4. Search for `mixed content`, `EnsureCoreWebView2Async`, `PostWebMessageAsString`, `MarkItDown`, and `evt-00001`.
5. Verify that the duplicate file produces the same content hash while preserving its own file path metadata.
6. Feed the XML path fixtures into the incremental parser and confirm that deleted paths are not re-indexed.

All content is synthetic and should be treated as test data rather than product documentation.
