WebView Indexing Field Guide

*Conversion notes, lifecycle observations, and search metadata*

This guide collects implementation notes for converting mixed WebView research files into searchable text. It describes the evidence expected from source files, the metadata that should survive conversion, and the observations that help diagnose indexing results.

The document intentionally includes headings, tables, code fragments, URLs, repeated terminology, and long paragraphs. Those structures should remain recognizable after conversion so downstream chunking and semantic search can be evaluated against the original content.

# Source evidence

A source record may contain a sheet name, section title, issue label, platform, status, and a free-form note. Missing values should remain missing rather than becoming plausible defaults. A converter should preserve the words around a missing field because the surrounding context often explains the intended meaning.

| **Field** | **Example** | **Conversion expectation** |
| --- | --- | --- |
| Platform | Android | Keep as searchable text |
| Issue | Mixed content not loading | Keep exact wording |
| Status | Investigating | Keep value and nearby section |
| Reference | https://example.test/webview/1001 | Keep URL text |

# React Native WebView 1

This section records observation 1. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 1

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 20 | 50 | Measured after reload |
| Payload KB | 5 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# React Native WebView 2

This section records observation 2. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# React Native WebView 3

This section records observation 3. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 3

# WPF WebView2 4

This section records observation 4. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 41 | 62 | Measured after reload |
| Payload KB | 14 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# WPF WebView2 5

This section records observation 5. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 5

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# WPF WebView2 6

This section records observation 6. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Security review 7

This section records observation 7. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 7

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 62 | 74 | Measured after reload |
| Payload KB | 23 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Security review 8

This section records observation 8. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Security review 9

This section records observation 9. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 9

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Performance review 10

This section records observation 10. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 83 | 86 | Measured after reload |
| Payload KB | 32 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Performance review 11

This section records observation 11. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 11

# Performance review 12

This section records observation 12. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Index metadata 13

This section records observation 13. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 13

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 104 | 98 | Measured after reload |
| Payload KB | 41 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Index metadata 14

This section records observation 14. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Index metadata 15

This section records observation 15. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 15

# Search behavior 16

This section records observation 16. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 125 | 110 | Measured after reload |
| Payload KB | 50 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Search behavior 17

This section records observation 17. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 17

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Search behavior 18

This section records observation 18. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# React Native WebView 19

This section records observation 19. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 19

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 146 | 122 | Measured after reload |
| Payload KB | 59 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# React Native WebView 20

This section records observation 20. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# React Native WebView 21

This section records observation 21. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 21

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# WPF WebView2 22

This section records observation 22. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 167 | 134 | Measured after reload |
| Payload KB | 68 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# WPF WebView2 23

This section records observation 23. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 23

# WPF WebView2 24

This section records observation 24. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Security review 25

This section records observation 25. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 25

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 188 | 146 | Measured after reload |
| Payload KB | 77 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Security review 26

This section records observation 26. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Security review 27

This section records observation 27. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 27

# Performance review 28

This section records observation 28. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 209 | 158 | Measured after reload |
| Payload KB | 86 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Performance review 29

This section records observation 29. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 29

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Performance review 30

This section records observation 30. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Index metadata 31

This section records observation 31. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 31

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 230 | 170 | Measured after reload |
| Payload KB | 95 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Index metadata 32

This section records observation 32. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Index metadata 33

This section records observation 33. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 33

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Search behavior 34

This section records observation 34. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 251 | 182 | Measured after reload |
| Payload KB | 104 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Search behavior 35

This section records observation 35. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 35

# Search behavior 36

This section records observation 36. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# React Native WebView 37

This section records observation 37. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 37

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 272 | 194 | Measured after reload |
| Payload KB | 113 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# React Native WebView 38

This section records observation 38. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# React Native WebView 39

This section records observation 39. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 39

# WPF WebView2 40

This section records observation 40. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 293 | 206 | Measured after reload |
| Payload KB | 122 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# WPF WebView2 41

This section records observation 41. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 41

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# WPF WebView2 42

This section records observation 42. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Security review 43

This section records observation 43. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

const bridgeMessage = { id: 'evt-00001', status: 'queued' };
// reference item 43

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 314 | 218 | Measured after reload |
| Payload KB | 131 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Security review 44

This section records observation 44. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

# Security review 45

This section records observation 45. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

await webView.EnsureCoreWebView2Async(null);
// reference item 45

Reference URL: https://developer.microsoft.com/en-us/microsoft-edge/webview2/. Related URL: https://github.com/react-native-webview/react-native-webview. The URLs are part of the source evidence and should remain visible in the converted text.

# Performance review 46

This section records observation 46. React Native uses a native web view underneath the JavaScript surface, while WPF WebView2 depends on an embedded Chromium runtime and a profile directory. The visible behavior can change after navigation, reload, offline transitions, or a change in the security policy. The indexing pipeline should preserve those conditions so a search result remains explainable.

The same terminology may appear in a table, a short note, and a code fragment. The relation between those pieces matters. A chunk that keeps only the code line can answer a syntax query but lose the platform, risk, and reproduction details. A chunk that keeps only the prose can miss the exact method name used by an engineer.

| **Measure** | **Observed** | **Expected** | **Note** |
| --- | --- | --- | --- |
| Latency ms | 335 | 230 | Measured after reload |
| Payload KB | 140 | bounded | Large payloads may cross chunk boundaries |
| Status | open | tracked | Keep the label unchanged |

# Metadata and incremental indexing

A converted chunk should retain file path, file name, extension, sheet or section context where available, chunk index, chunk total, modified time, and indexed time. Changed files should be removed from the vector store before re-indexing. Deleted files should not reappear during the normal folder traversal.

| **Metadata** | **Example** | **Why it matters** |
| --- | --- | --- |
| file\_path | \\pc135\D\Desktop\SampleFolders\04\_office\Messy\_WebView\_Research.xlsx | Trace result to source |
| file\_extension | .xlsx | Filter and classify |
| chunk\_index | 3 | Open the matching excerpt |
| chunk\_total | 12 | Show context and progress |
| file\_modified\_at | 2026-10-03T00:00:00Z | Skip unchanged files |

A path list may contain a drive-letter path from a backup export. The path normalizer should convert it to the configured UNC representation while keeping enough information to troubleshoot the mapping. Repeated paths in a changed list should be handled idempotently.

# Search terms

Useful exact terms for regression searches include mixed content, EnsureCoreWebView2Async, PostWebMessageAsString, injected JavaScript, file\_modified\_at, chunk\_index, MarkItDown, and evt-00001. A semantic search query may use a synonym, but the returned excerpt should still provide the original technical phrase.

* **Query fixture 1:** mixed content security risk on Android
* **Query fixture 2:** large bridge payload latency
* **Query fixture 3:** WPF runtime initialization
* **Query fixture 4:** sheet name preservation
* **Query fixture 5:** duplicate content hash
* **Query fixture 6:** changed and deleted XML paths
* **Query fixture 7:** mixed content security risk on Android
* **Query fixture 8:** large bridge payload latency
* **Query fixture 9:** WPF runtime initialization
* **Query fixture 10:** sheet name preservation
* **Query fixture 11:** duplicate content hash
* **Query fixture 12:** changed and deleted XML paths
* **Query fixture 13:** mixed content security risk on Android
* **Query fixture 14:** large bridge payload latency
* **Query fixture 15:** WPF runtime initialization
* **Query fixture 16:** sheet name preservation
* **Query fixture 17:** duplicate content hash
* **Query fixture 18:** changed and deleted XML paths