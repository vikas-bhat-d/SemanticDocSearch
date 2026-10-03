<!-- Slide number: 1 -->
WebView indexing test corpus
Mixed Office files, structured exports, and search metadata
The deck contains repeated technical terms, code fragments, URLs, and metadata examples so slide conversion can be checked alongside Excel, DOCX, PDF, HTML, and plain-text fixtures.
1 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 2 -->
Source file variety
The corpus includes a large messy workbook, a small reference workbook, long Markdown, plain logs, CSV, TSV, JSON, XML, HTML, DOCX, PDF, SVG, and edge-case files. Each file keeps a distinct path and extension for indexing tests.
2 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 3 -->
React Native observations
Mixed content can fail on Android while injected JavaScript behaves differently on iOS. Search should find the exact phrase mixed content and return the platform context, issue status, and related URL.
npm install react-native-webview
webView.injectJavaScript(script);
3 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 4 -->
WPF WebView2 observations
The Evergreen runtime and the native lifecycle matter during initialization. A converted excerpt should keep the method name, the surrounding note, and the runtime download URL.
await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.Navigate(uri);
4 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 5 -->
Bridge payload behavior
PostWebMessageAsString and ExecuteScriptAsync appear in multiple source files. Repeated mentions are intentional so semantic search and duplicate-content handling can be compared.
webView.CoreWebView2.PostWebMessageAsString(payload);
await CoreWebView2.ExecuteScriptAsync(js);
5 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 6 -->
Chunk metadata
Each result should keep file_path, file_name, file_extension, chunk_index, chunk_total, file_modified_at, and indexed_at. Sheet and section context should remain near the converted content.
file_path   \\pc135\D\Desktop\SampleFolders\file.xlsx
chunk_index   3
chunk_total   12
file_modified_at   2026-10-03T00:00:00Z
6 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 7 -->
Incremental indexing
The changed and deleted XML fixtures use drive-letter paths from a backup export. The parser should normalize paths, delete old points, and avoid re-indexing deleted files during traversal.
changed_paths.xml
deleted_paths.xml
"E:\\Winman Backup\\2026-10-03\\PC135(D.)\\Desktop\\SampleFolders\\file.xlsx"
7 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.

<!-- Slide number: 8 -->
Regression queries
Search terms include mixed content, EnsureCoreWebView2Async, PostWebMessageAsString, MarkItDown, file_modified_at, duplicate content hash, changed and deleted XML paths, and Unicode café 東京.
All content is synthetic test data.
8 / 8

### Notes:
Synthetic conversion fixture. Preserve visible slide text and speaker-note text when testing PPTX conversion.