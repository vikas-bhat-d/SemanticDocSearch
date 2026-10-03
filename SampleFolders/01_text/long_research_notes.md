# WebView Research Notes
This file is intentionally long and repetitive so chunking can be tested across stable headings.

## React Native observations 1

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 1.

- platform: Android
- status: open
- reference: https://example.test/webview/1000

```text
bridge event payload {"id": 0, "status": "queued"}
```

| Field | Value | Note |
|---|---|---|
| latency_ms | 20 | measured after reload |
| payload_kb | 5 | includes Unicode: café 東京 |

## React Native observations 2

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 2.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1001

## React Native observations 3

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 3.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1002

## React Native observations 4

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 4.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1003

## React Native observations 5

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 5.

- platform: Android
- status: open
- reference: https://example.test/webview/1004

## React Native observations 6

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 6.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1005

## WPF WebView2 observations 7

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 7.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1006

## WPF WebView2 observations 8

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 8.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1007

## WPF WebView2 observations 9

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 9.

- platform: Android
- status: open
- reference: https://example.test/webview/1008

## WPF WebView2 observations 10

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 10.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1009

```text
bridge event payload {"id": 9, "status": "queued"}
```

## WPF WebView2 observations 11

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 11.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1010

## WPF WebView2 observations 12

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 12.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1011

## Security questions 13

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 13.

- platform: Android
- status: open
- reference: https://example.test/webview/1012

## Security questions 14

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 14.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1013

| Field | Value | Note |
|---|---|---|
| latency_ms | 33 | measured after reload |
| payload_kb | 31 | includes Unicode: café 東京 |

## Security questions 15

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 15.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1014

## Security questions 16

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 16.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1015

## Security questions 17

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 17.

- platform: Android
- status: open
- reference: https://example.test/webview/1016

## Security questions 18

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 18.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1017

## Performance notes 19

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 19.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1018

```text
bridge event payload {"id": 18, "status": "queued"}
```

## Performance notes 20

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 20.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1019

## Performance notes 21

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 21.

- platform: Android
- status: open
- reference: https://example.test/webview/1020

## Performance notes 22

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 22.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1021

## Performance notes 23

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 23.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1022

## Performance notes 24

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 24.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1023

## Indexing behavior 25

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 25.

- platform: Android
- status: open
- reference: https://example.test/webview/1024

## Indexing behavior 26

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 26.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1025

## Indexing behavior 27

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 27.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1026

| Field | Value | Note |
|---|---|---|
| latency_ms | 46 | measured after reload |
| payload_kb | 57 | includes Unicode: café 東京 |

## Indexing behavior 28

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 28.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1027

```text
bridge event payload {"id": 27, "status": "queued"}
```

## Indexing behavior 29

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 29.

- platform: Android
- status: open
- reference: https://example.test/webview/1028

## Indexing behavior 30

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 30.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1029

## Loose follow-up 31

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 31.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1030

## Loose follow-up 32

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 32.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1031

## Loose follow-up 33

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 33.

- platform: Android
- status: open
- reference: https://example.test/webview/1032

## Loose follow-up 34

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 34.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1033

## Loose follow-up 35

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 35.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1034

## Loose follow-up 36

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 36.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1035

## React Native observations 37

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 37.

- platform: Android
- status: open
- reference: https://example.test/webview/1036

```text
bridge event payload {"id": 36, "status": "queued"}
```

## React Native observations 38

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 38.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1037

## React Native observations 39

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 39.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1038

## React Native observations 40

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 40.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1039

| Field | Value | Note |
|---|---|---|
| latency_ms | 59 | measured after reload |
| payload_kb | 83 | includes Unicode: café 東京 |

## React Native observations 41

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 41.

- platform: Android
- status: open
- reference: https://example.test/webview/1040

## React Native observations 42

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 42.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1041

## WPF WebView2 observations 43

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 43.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1042

## WPF WebView2 observations 44

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 44.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1043

## WPF WebView2 observations 45

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 45.

- platform: Android
- status: open
- reference: https://example.test/webview/1044

## WPF WebView2 observations 46

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 46.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1045

```text
bridge event payload {"id": 45, "status": "queued"}
```

## WPF WebView2 observations 47

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 47.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1046

## WPF WebView2 observations 48

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 48.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1047

## Security questions 49

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 49.

- platform: Android
- status: open
- reference: https://example.test/webview/1048

## Security questions 50

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 50.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1049

## Security questions 51

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 51.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1050

## Security questions 52

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 52.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1051

## Security questions 53

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 53.

- platform: Android
- status: open
- reference: https://example.test/webview/1052

| Field | Value | Note |
|---|---|---|
| latency_ms | 72 | measured after reload |
| payload_kb | 109 | includes Unicode: café 東京 |

## Security questions 54

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 54.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1053

## Performance notes 55

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 55.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1054

```text
bridge event payload {"id": 54, "status": "queued"}
```

## Performance notes 56

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 56.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1055

## Performance notes 57

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 57.

- platform: Android
- status: open
- reference: https://example.test/webview/1056

## Performance notes 58

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 58.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1057

## Performance notes 59

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 59.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1058

## Performance notes 60

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 60.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1059

## Indexing behavior 61

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 61.

- platform: Android
- status: open
- reference: https://example.test/webview/1060

## Indexing behavior 62

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 62.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1061

## Indexing behavior 63

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 63.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1062

## Indexing behavior 64

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 64.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1063

```text
bridge event payload {"id": 63, "status": "queued"}
```

## Indexing behavior 65

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 65.

- platform: Android
- status: open
- reference: https://example.test/webview/1064

## Indexing behavior 66

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 66.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1065

| Field | Value | Note |
|---|---|---|
| latency_ms | 85 | measured after reload |
| payload_kb | 135 | includes Unicode: café 東京 |

## Loose follow-up 67

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 67.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1066

## Loose follow-up 68

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 68.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1067

## Loose follow-up 69

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 69.

- platform: Android
- status: open
- reference: https://example.test/webview/1068

## Loose follow-up 70

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 70.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1069

## Loose follow-up 71

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 71.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1070

## Loose follow-up 72

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 72.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1071

## React Native observations 73

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 73.

- platform: Android
- status: open
- reference: https://example.test/webview/1072

```text
bridge event payload {"id": 72, "status": "queued"}
```

## React Native observations 74

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 74.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1073

## React Native observations 75

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 75.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1074

## React Native observations 76

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 76.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1075

## React Native observations 77

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 77.

- platform: Android
- status: open
- reference: https://example.test/webview/1076

## React Native observations 78

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 78.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1077

## WPF WebView2 observations 79

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 79.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1078

| Field | Value | Note |
|---|---|---|
| latency_ms | 98 | measured after reload |
| payload_kb | 161 | includes Unicode: café 東京 |

## WPF WebView2 observations 80

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 80.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1079

## WPF WebView2 observations 81

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 81.

- platform: Android
- status: open
- reference: https://example.test/webview/1080

## WPF WebView2 observations 82

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 82.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1081

```text
bridge event payload {"id": 81, "status": "queued"}
```

## WPF WebView2 observations 83

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 83.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1082

## WPF WebView2 observations 84

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 84.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1083

## Security questions 85

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 85.

- platform: Android
- status: open
- reference: https://example.test/webview/1084

## Security questions 86

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 86.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1085

## Security questions 87

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 87.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1086

## Security questions 88

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 88.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1087

## Security questions 89

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 89.

- platform: Android
- status: open
- reference: https://example.test/webview/1088

## Security questions 90

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 90.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1089

## Performance notes 91

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 91.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1090

```text
bridge event payload {"id": 90, "status": "queued"}
```

## Performance notes 92

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 92.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1091

| Field | Value | Note |
|---|---|---|
| latency_ms | 111 | measured after reload |
| payload_kb | 187 | includes Unicode: café 東京 |

## Performance notes 93

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 93.

- platform: Android
- status: open
- reference: https://example.test/webview/1092

## Performance notes 94

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 94.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1093

## Performance notes 95

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 95.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1094

## Performance notes 96

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 96.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1095

## Indexing behavior 97

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 97.

- platform: Android
- status: open
- reference: https://example.test/webview/1096

## Indexing behavior 98

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 98.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1097

## Indexing behavior 99

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 99.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1098

## Indexing behavior 100

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 100.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1099

```text
bridge event payload {"id": 99, "status": "queued"}
```

## Indexing behavior 101

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 101.

- platform: Android
- status: open
- reference: https://example.test/webview/1100

## Indexing behavior 102

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 102.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1101

## Loose follow-up 103

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 103.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1102

## Loose follow-up 104

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 104.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1103

## Loose follow-up 105

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 105.

- platform: Android
- status: open
- reference: https://example.test/webview/1104

| Field | Value | Note |
|---|---|---|
| latency_ms | 124 | measured after reload |
| payload_kb | 213 | includes Unicode: café 東京 |

## Loose follow-up 106

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 106.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1105

## Loose follow-up 107

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 107.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1106

## Loose follow-up 108

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 108.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1107

## React Native observations 109

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 109.

- platform: Android
- status: open
- reference: https://example.test/webview/1108

```text
bridge event payload {"id": 108, "status": "queued"}
```

## React Native observations 110

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 110.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1109

## React Native observations 111

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 111.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1110

## React Native observations 112

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 112.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1111

## React Native observations 113

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 113.

- platform: Android
- status: open
- reference: https://example.test/webview/1112

## React Native observations 114

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 114.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1113

## WPF WebView2 observations 115

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 115.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1114

## WPF WebView2 observations 116

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 116.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1115

## WPF WebView2 observations 117

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 117.

- platform: Android
- status: open
- reference: https://example.test/webview/1116

## WPF WebView2 observations 118

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 118.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1117

```text
bridge event payload {"id": 117, "status": "queued"}
```

| Field | Value | Note |
|---|---|---|
| latency_ms | 137 | measured after reload |
| payload_kb | 239 | includes Unicode: café 東京 |

## WPF WebView2 observations 119

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 119.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1118

## WPF WebView2 observations 120

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 120.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1119

## Security questions 121

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 121.

- platform: Android
- status: open
- reference: https://example.test/webview/1120

## Security questions 122

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 122.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1121

## Security questions 123

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 123.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1122

## Security questions 124

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 124.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1123

## Security questions 125

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 125.

- platform: Android
- status: open
- reference: https://example.test/webview/1124

## Security questions 126

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 126.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1125

## Performance notes 127

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 127.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1126

```text
bridge event payload {"id": 126, "status": "queued"}
```

## Performance notes 128

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 128.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1127

## Performance notes 129

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 129.

- platform: Android
- status: open
- reference: https://example.test/webview/1128

## Performance notes 130

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 130.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1129

## Performance notes 131

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 131.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1130

| Field | Value | Note |
|---|---|---|
| latency_ms | 150 | measured after reload |
| payload_kb | 265 | includes Unicode: café 東京 |

## Performance notes 132

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 132.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1131

## Indexing behavior 133

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 133.

- platform: Android
- status: open
- reference: https://example.test/webview/1132

## Indexing behavior 134

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 134.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1133

## Indexing behavior 135

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 135.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1134

## Indexing behavior 136

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 136.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1135

```text
bridge event payload {"id": 135, "status": "queued"}
```

## Indexing behavior 137

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 137.

- platform: Android
- status: open
- reference: https://example.test/webview/1136

## Indexing behavior 138

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 138.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1137

## Loose follow-up 139

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 139.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1138

## Loose follow-up 140

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 140.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1139

## Loose follow-up 141

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 141.

- platform: Android
- status: open
- reference: https://example.test/webview/1140

## Loose follow-up 142

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 142.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1141

## Loose follow-up 143

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 143.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1142

## Loose follow-up 144

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 144.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1143

| Field | Value | Note |
|---|---|---|
| latency_ms | 163 | measured after reload |
| payload_kb | 291 | includes Unicode: café 東京 |

## React Native observations 145

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 145.

- platform: Android
- status: open
- reference: https://example.test/webview/1144

```text
bridge event payload {"id": 144, "status": "queued"}
```

## React Native observations 146

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 146.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1145

## React Native observations 147

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 147.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1146

## React Native observations 148

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 148.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1147

## React Native observations 149

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 149.

- platform: Android
- status: open
- reference: https://example.test/webview/1148

## React Native observations 150

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 150.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1149

## WPF WebView2 observations 151

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 151.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1150

## WPF WebView2 observations 152

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 152.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1151

## WPF WebView2 observations 153

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 153.

- platform: Android
- status: open
- reference: https://example.test/webview/1152

## WPF WebView2 observations 154

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 154.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1153

```text
bridge event payload {"id": 153, "status": "queued"}
```

## WPF WebView2 observations 155

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 155.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1154

## WPF WebView2 observations 156

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 156.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1155

## Security questions 157

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 157.

- platform: Android
- status: open
- reference: https://example.test/webview/1156

| Field | Value | Note |
|---|---|---|
| latency_ms | 176 | measured after reload |
| payload_kb | 317 | includes Unicode: café 東京 |

## Security questions 158

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 158.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1157

## Security questions 159

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 159.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1158

## Security questions 160

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 160.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1159

## Security questions 161

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 161.

- platform: Android
- status: open
- reference: https://example.test/webview/1160

## Security questions 162

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 162.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1161

## Performance notes 163

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 163.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1162

```text
bridge event payload {"id": 162, "status": "queued"}
```

## Performance notes 164

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 164.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1163

## Performance notes 165

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 165.

- platform: Android
- status: open
- reference: https://example.test/webview/1164

## Performance notes 166

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 166.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1165

## Performance notes 167

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 167.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1166

## Performance notes 168

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 168.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1167

## Indexing behavior 169

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 169.

- platform: Android
- status: open
- reference: https://example.test/webview/1168

## Indexing behavior 170

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 170.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1169

| Field | Value | Note |
|---|---|---|
| latency_ms | 189 | measured after reload |
| payload_kb | 343 | includes Unicode: café 東京 |

## Indexing behavior 171

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 171.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1170

## Indexing behavior 172

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 172.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1171

```text
bridge event payload {"id": 171, "status": "queued"}
```

## Indexing behavior 173

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 173.

- platform: Android
- status: open
- reference: https://example.test/webview/1172

## Indexing behavior 174

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 174.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1173

## Loose follow-up 175

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 175.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1174

## Loose follow-up 176

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 176.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1175

## Loose follow-up 177

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 177.

- platform: Android
- status: open
- reference: https://example.test/webview/1176

## Loose follow-up 178

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 178.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1177

## Loose follow-up 179

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 179.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1178

## Loose follow-up 180

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 180.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1179

## React Native observations 181

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 181.

- platform: Android
- status: open
- reference: https://example.test/webview/1180

```text
bridge event payload {"id": 180, "status": "queued"}
```

## React Native observations 182

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 182.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1181

## React Native observations 183

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 183.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1182

| Field | Value | Note |
|---|---|---|
| latency_ms | 202 | measured after reload |
| payload_kb | 369 | includes Unicode: café 東京 |

## React Native observations 184

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 184.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1183

## React Native observations 185

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 185.

- platform: Android
- status: open
- reference: https://example.test/webview/1184

## React Native observations 186

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 186.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1185

## WPF WebView2 observations 187

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 187.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1186

## WPF WebView2 observations 188

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 188.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1187

## WPF WebView2 observations 189

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 189.

- platform: Android
- status: open
- reference: https://example.test/webview/1188

## WPF WebView2 observations 190

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 190.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1189

```text
bridge event payload {"id": 189, "status": "queued"}
```

## WPF WebView2 observations 191

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 191.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1190

## WPF WebView2 observations 192

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 192.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1191

## Security questions 193

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 193.

- platform: Android
- status: open
- reference: https://example.test/webview/1192

## Security questions 194

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 194.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1193

## Security questions 195

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 195.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1194

## Security questions 196

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 196.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1195

| Field | Value | Note |
|---|---|---|
| latency_ms | 215 | measured after reload |
| payload_kb | 395 | includes Unicode: café 東京 |

## Security questions 197

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 197.

- platform: Android
- status: open
- reference: https://example.test/webview/1196

## Security questions 198

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 198.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1197

## Performance notes 199

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 199.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1198

```text
bridge event payload {"id": 198, "status": "queued"}
```

## Performance notes 200

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 200.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1199

## Performance notes 201

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 201.

- platform: Android
- status: open
- reference: https://example.test/webview/1200

## Performance notes 202

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 202.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1201

## Performance notes 203

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 203.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1202

## Performance notes 204

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 204.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1203

## Indexing behavior 205

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 205.

- platform: Android
- status: open
- reference: https://example.test/webview/1204

## Indexing behavior 206

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 206.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1205

## Indexing behavior 207

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 207.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1206

## Indexing behavior 208

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 208.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1207

```text
bridge event payload {"id": 207, "status": "queued"}
```

## Indexing behavior 209

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 209.

- platform: Android
- status: open
- reference: https://example.test/webview/1208

| Field | Value | Note |
|---|---|---|
| latency_ms | 228 | measured after reload |
| payload_kb | 421 | includes Unicode: café 東京 |

## Indexing behavior 210

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 210.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1209

## Loose follow-up 211

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 211.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1210

## Loose follow-up 212

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 212.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1211

## Loose follow-up 213

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 213.

- platform: Android
- status: open
- reference: https://example.test/webview/1212

## Loose follow-up 214

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 214.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1213

## Loose follow-up 215

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 215.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1214

## Loose follow-up 216

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 216.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1215

## React Native observations 217

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 217.

- platform: Android
- status: open
- reference: https://example.test/webview/1216

```text
bridge event payload {"id": 216, "status": "queued"}
```

## React Native observations 218

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 218.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1217

## React Native observations 219

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 219.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1218

## React Native observations 220

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 220.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1219

## React Native observations 221

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 221.

- platform: Android
- status: open
- reference: https://example.test/webview/1220

## React Native observations 222

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 222.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1221

| Field | Value | Note |
|---|---|---|
| latency_ms | 241 | measured after reload |
| payload_kb | 447 | includes Unicode: café 東京 |

## WPF WebView2 observations 223

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 223.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1222

## WPF WebView2 observations 224

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 224.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1223

## WPF WebView2 observations 225

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 225.

- platform: Android
- status: open
- reference: https://example.test/webview/1224

## WPF WebView2 observations 226

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 226.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1225

```text
bridge event payload {"id": 225, "status": "queued"}
```

## WPF WebView2 observations 227

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 227.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1226

## WPF WebView2 observations 228

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 228.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1227

## Security questions 229

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 229.

- platform: Android
- status: open
- reference: https://example.test/webview/1228

## Security questions 230

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 230.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1229

## Security questions 231

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 231.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1230

## Security questions 232

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 232.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1231

## Security questions 233

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 233.

- platform: Android
- status: open
- reference: https://example.test/webview/1232

## Security questions 234

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 234.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1233

## Performance notes 235

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 235.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1234

```text
bridge event payload {"id": 234, "status": "queued"}
```

| Field | Value | Note |
|---|---|---|
| latency_ms | 254 | measured after reload |
| payload_kb | 473 | includes Unicode: café 東京 |

## Performance notes 236

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 236.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1235

## Performance notes 237

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 237.

- platform: Android
- status: open
- reference: https://example.test/webview/1236

## Performance notes 238

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 238.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1237

## Performance notes 239

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 239.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1238

## Performance notes 240

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 240.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1239

## Indexing behavior 241

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 241.

- platform: Android
- status: open
- reference: https://example.test/webview/1240

## Indexing behavior 242

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 242.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1241

## Indexing behavior 243

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 243.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1242

## Indexing behavior 244

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 244.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1243

```text
bridge event payload {"id": 243, "status": "queued"}
```

## Indexing behavior 245

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 245.

- platform: Android
- status: open
- reference: https://example.test/webview/1244

## Indexing behavior 246

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 246.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1245

## Loose follow-up 247

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 247.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1246

## Loose follow-up 248

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 248.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1247

| Field | Value | Note |
|---|---|---|
| latency_ms | 267 | measured after reload |
| payload_kb | 499 | includes Unicode: café 東京 |

## Loose follow-up 249

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 249.

- platform: Android
- status: open
- reference: https://example.test/webview/1248

## Loose follow-up 250

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 250.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1249

## Loose follow-up 251

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 251.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1250

## Loose follow-up 252

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 252.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1251

## React Native observations 253

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 253.

- platform: Android
- status: open
- reference: https://example.test/webview/1252

```text
bridge event payload {"id": 252, "status": "queued"}
```

## React Native observations 254

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 254.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1253

## React Native observations 255

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 255.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1254

## React Native observations 256

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 256.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1255

## React Native observations 257

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 257.

- platform: Android
- status: open
- reference: https://example.test/webview/1256

## React Native observations 258

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 258.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1257

## WPF WebView2 observations 259

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 259.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1258

## WPF WebView2 observations 260

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 260.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1259

## WPF WebView2 observations 261

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 261.

- platform: Android
- status: open
- reference: https://example.test/webview/1260

| Field | Value | Note |
|---|---|---|
| latency_ms | 280 | measured after reload |
| payload_kb | 525 | includes Unicode: café 東京 |

## WPF WebView2 observations 262

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 262.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1261

```text
bridge event payload {"id": 261, "status": "queued"}
```

## WPF WebView2 observations 263

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 263.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1262

## WPF WebView2 observations 264

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 264.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1263

## Security questions 265

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 265.

- platform: Android
- status: open
- reference: https://example.test/webview/1264

## Security questions 266

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 266.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1265

## Security questions 267

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 267.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1266

## Security questions 268

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 268.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1267

## Security questions 269

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 269.

- platform: Android
- status: open
- reference: https://example.test/webview/1268

## Security questions 270

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 270.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1269

## Performance notes 271

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 271.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1270

```text
bridge event payload {"id": 270, "status": "queued"}
```

## Performance notes 272

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 272.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1271

## Performance notes 273

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 273.

- platform: Android
- status: open
- reference: https://example.test/webview/1272

## Performance notes 274

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 274.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1273

| Field | Value | Note |
|---|---|---|
| latency_ms | 293 | measured after reload |
| payload_kb | 551 | includes Unicode: café 東京 |

## Performance notes 275

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 275.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1274

## Performance notes 276

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 276.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1275

## Indexing behavior 277

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 277.

- platform: Android
- status: open
- reference: https://example.test/webview/1276

## Indexing behavior 278

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 278.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1277

## Indexing behavior 279

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 279.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1278

## Indexing behavior 280

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 280.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1279

```text
bridge event payload {"id": 279, "status": "queued"}
```

## Indexing behavior 281

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 281.

- platform: Android
- status: open
- reference: https://example.test/webview/1280

## Indexing behavior 282

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 282.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1281

## Loose follow-up 283

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 283.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1282

## Loose follow-up 284

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 284.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1283

## Loose follow-up 285

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 285.

- platform: Android
- status: open
- reference: https://example.test/webview/1284

## Loose follow-up 286

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 286.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1285

## Loose follow-up 287

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 287.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1286

| Field | Value | Note |
|---|---|---|
| latency_ms | 306 | measured after reload |
| payload_kb | 577 | includes Unicode: café 東京 |

## Loose follow-up 288

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 288.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1287

## React Native observations 289

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 289.

- platform: Android
- status: open
- reference: https://example.test/webview/1288

```text
bridge event payload {"id": 288, "status": "queued"}
```

## React Native observations 290

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 290.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1289

## React Native observations 291

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 291.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1290

## React Native observations 292

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 292.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1291

## React Native observations 293

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 293.

- platform: Android
- status: open
- reference: https://example.test/webview/1292

## React Native observations 294

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 294.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1293

## WPF WebView2 observations 295

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 295.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1294

## WPF WebView2 observations 296

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 296.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1295

## WPF WebView2 observations 297

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 297.

- platform: Android
- status: open
- reference: https://example.test/webview/1296

## WPF WebView2 observations 298

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 298.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1297

```text
bridge event payload {"id": 297, "status": "queued"}
```

## WPF WebView2 observations 299

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 299.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1298

## WPF WebView2 observations 300

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 300.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1299

| Field | Value | Note |
|---|---|---|
| latency_ms | 319 | measured after reload |
| payload_kb | 603 | includes Unicode: café 東京 |

## Security questions 301

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 301.

- platform: Android
- status: open
- reference: https://example.test/webview/1300

## Security questions 302

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 302.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1301

## Security questions 303

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 303.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1302

## Security questions 304

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 304.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1303

## Security questions 305

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 305.

- platform: Android
- status: open
- reference: https://example.test/webview/1304

## Security questions 306

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 306.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1305

## Performance notes 307

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 307.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1306

```text
bridge event payload {"id": 306, "status": "queued"}
```

## Performance notes 308

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 308.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1307

## Performance notes 309

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 309.

- platform: Android
- status: open
- reference: https://example.test/webview/1308

## Performance notes 310

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 310.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1309

## Performance notes 311

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 311.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1310

## Performance notes 312

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 312.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1311

## Indexing behavior 313

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 313.

- platform: Android
- status: open
- reference: https://example.test/webview/1312

| Field | Value | Note |
|---|---|---|
| latency_ms | 332 | measured after reload |
| payload_kb | 629 | includes Unicode: café 東京 |

## Indexing behavior 314

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 314.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1313

## Indexing behavior 315

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 315.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1314

## Indexing behavior 316

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 316.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1315

```text
bridge event payload {"id": 315, "status": "queued"}
```

## Indexing behavior 317

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 317.

- platform: Android
- status: open
- reference: https://example.test/webview/1316

## Indexing behavior 318

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 318.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1317

## Loose follow-up 319

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 319.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1318

## Loose follow-up 320

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 320.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1319

## Loose follow-up 321

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 321.

- platform: Android
- status: open
- reference: https://example.test/webview/1320

## Loose follow-up 322

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 322.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1321

## Loose follow-up 323

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 323.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1322

## Loose follow-up 324

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 324.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1323

## React Native observations 325

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 325.

- platform: Android
- status: open
- reference: https://example.test/webview/1324

```text
bridge event payload {"id": 324, "status": "queued"}
```

## React Native observations 326

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 326.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1325

| Field | Value | Note |
|---|---|---|
| latency_ms | 345 | measured after reload |
| payload_kb | 655 | includes Unicode: café 東京 |

## React Native observations 327

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 327.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1326

## React Native observations 328

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 328.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1327

## React Native observations 329

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 329.

- platform: Android
- status: open
- reference: https://example.test/webview/1328

## React Native observations 330

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 330.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1329

## WPF WebView2 observations 331

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 331.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1330

## WPF WebView2 observations 332

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 332.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1331

## WPF WebView2 observations 333

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 333.

- platform: Android
- status: open
- reference: https://example.test/webview/1332

## WPF WebView2 observations 334

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 334.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1333

```text
bridge event payload {"id": 333, "status": "queued"}
```

## WPF WebView2 observations 335

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 335.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1334

## WPF WebView2 observations 336

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 336.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1335

## Security questions 337

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 337.

- platform: Android
- status: open
- reference: https://example.test/webview/1336

## Security questions 338

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 338.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1337

## Security questions 339

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 339.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1338

| Field | Value | Note |
|---|---|---|
| latency_ms | 358 | measured after reload |
| payload_kb | 681 | includes Unicode: café 東京 |

## Security questions 340

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 340.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1339

## Security questions 341

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 341.

- platform: Android
- status: open
- reference: https://example.test/webview/1340

## Security questions 342

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 342.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1341

## Performance notes 343

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 343.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1342

```text
bridge event payload {"id": 342, "status": "queued"}
```

## Performance notes 344

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 344.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1343

## Performance notes 345

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 345.

- platform: Android
- status: open
- reference: https://example.test/webview/1344

## Performance notes 346

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 346.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1345

## Performance notes 347

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 347.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1346

## Performance notes 348

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 348.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1347

## Indexing behavior 349

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 349.

- platform: Android
- status: open
- reference: https://example.test/webview/1348

## Indexing behavior 350

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 350.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1349

## Indexing behavior 351

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 351.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1350

## Indexing behavior 352

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 352.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1351

```text
bridge event payload {"id": 351, "status": "queued"}
```

| Field | Value | Note |
|---|---|---|
| latency_ms | 371 | measured after reload |
| payload_kb | 707 | includes Unicode: café 東京 |

## Indexing behavior 353

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 353.

- platform: Android
- status: open
- reference: https://example.test/webview/1352

## Indexing behavior 354

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 354.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1353

## Loose follow-up 355

React Native WebView uses a native view underneath the JavaScript surface, so lifecycle timing affects both navigation and bridge delivery. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 355.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1354

## Loose follow-up 356

WPF WebView2 depends on the Evergreen runtime and a user data folder whose permissions and profile state change the observed result. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 356.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1355

## Loose follow-up 357

MarkItDown conversion should retain enough context to connect a note with its sheet name, heading, file path, and nearby code fragment. The note includes a device-specific observation and a deliberately repeated phrase for deduplication tests. Reference item 357.

- platform: Android
- status: open
- reference: https://example.test/webview/1356

## Loose follow-up 358

A recursive splitter needs stable section boundaries because a long paragraph can otherwise separate the question from its reproduction details. The example contains a URL, a short code fragment, and a field that is intentionally missing. Reference item 358.

- platform: iOS
- status: investigating
- reference: https://example.test/webview/1357

## Loose follow-up 359

Incremental indexing should treat changed and deleted files differently while preserving the original path spelling in metadata. The expected behavior remains uncertain until the same scenario is reproduced after a reload. Reference item 359.

- platform: Windows
- status: resolved
- reference: https://example.test/webview/1358

## Loose follow-up 360

Blank rows and shifted cells are meaningful test inputs because they expose whether cleanup code assumes a rectangular table. Keep the wording intact during conversion because downstream search should find the exact technical terms. Reference item 360.

- platform: macOS
- status: needs reproduction
- reference: https://example.test/webview/1359

