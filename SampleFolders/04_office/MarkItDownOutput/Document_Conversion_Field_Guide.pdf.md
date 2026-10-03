Document Conversion Field Guide

Mixed Office files, metadata, and semantic indexing

This field guide describes the content that a conversion pipeline should preserve when it reads Office files, web
captures, and structured exports. It covers sheet context, code fragments, path metadata, incremental indexing, and
search-oriented chunk boundaries.

The guide includes repeated terms, code, URLs, tables, and long prose so a PDF converter can be checked against
both readable output and full-text extraction.

Source feature

Example

Expected result

Sheet name

RN_WebView

Appears before sheet content

Code

URL

Path

EnsureCoreWebView2Async

Remains searchable

https://example.test/webview/1001

Preserved as text

\\pc135\D\Desktop\SampleFolders\
file.xlsx

Retained in metadata

Document Conversion Field Guide

Page 1

Workbook context 1

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 1, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Metric

Value

Interpretation

Latency ms

Payload KB

20

5

Measured after reload

May cross a chunk boundary

Status

open

Keep source label

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

WebView lifecycle 2

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 2, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 3

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 3, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 4

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 4, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 5

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 5, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Document Conversion Field Guide

Page 2

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Incremental indexing 6

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 6, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

45

15

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Search verification 7

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 7, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 8

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 8, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 9

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 9, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Security observations 10

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 10, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can

Document Conversion Field Guide

Page 3

distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Performance logs 11

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 11, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

70

25

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Chunk metadata 12

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 12, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 13

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 13, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Search verification 14

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 14, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 15

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 15, included to create realistic page density and chunk boundaries. If the same

Document Conversion Field Guide

Page 4

phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 16

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 16, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

95

35

Measured after reload

May cross a chunk boundary

Status

open

Keep source label

Security observations 17

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 17, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Performance logs 18

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 18, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 19

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 19, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Incremental indexing 20

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away

Document Conversion Field Guide

Page 5

from the nearest table. This is field note 20, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 21

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 21, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Metric

Value

Interpretation

Latency ms

Payload KB

120

45

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Workbook context 22

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 22, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 23

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 23, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 24

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 24, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 25

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 25, included to create realistic page density and chunk boundaries. If the same

Document Conversion Field Guide

Page 6

phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Chunk metadata 26

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 26, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

145

55

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Incremental indexing 27

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 27, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 28

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 28, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Workbook context 29

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 29, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

WebView lifecycle 30

Document Conversion Field Guide

Page 7

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 30, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 31

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 31, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Latency ms

Payload KB

Status

Value

170

65

open

Interpretation

Measured after reload

May cross a chunk boundary

Keep source label

Performance logs 32

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 32, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 33

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 33, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Incremental indexing 34

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 34, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 35

Document Conversion Field Guide

Page 8

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 35, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 36

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 36, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

195

75

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

WebView lifecycle 37

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 37, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Security observations 38

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 38, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 39

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 39, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 40

Document Conversion Field Guide

Page 9

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 40, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 41

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 41, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Metric

Value

Interpretation

Latency ms

Payload KB

220

85

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Search verification 42

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 42, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 43

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 43, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 44

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 44, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 45

Document Conversion Field Guide

Page 10

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 45, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Performance logs 46

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 46, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Latency ms

Payload KB

Status

Value

245

95

open

Interpretation

Measured after reload

May cross a chunk boundary

Keep source label

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Chunk metadata 47

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 47, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 48

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 48, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 49

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 49, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);

Document Conversion Field Guide

Page 11

const chunk = { file_path, chunk_index, chunk_total };

Workbook context 50

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 50, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 51

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 51, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

270

105

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Security observations 52

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 52, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 53

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 53, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Chunk metadata 54

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 54, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Document Conversion Field Guide

Page 12

Incremental indexing 55

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 55, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Search verification 56

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 56, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

295

115

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Workbook context 57

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 57, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

WebView lifecycle 58

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 58, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 59

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 59, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Document Conversion Field Guide

Page 13

Performance logs 60

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 60, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 61

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 61, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Metric

Latency ms

Payload KB

Status

Value

320

125

open

Interpretation

Measured after reload

May cross a chunk boundary

Keep source label

Incremental indexing 62

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 62, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 63

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 63, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 64

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 64, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Document Conversion Field Guide

Page 14

WebView lifecycle 65

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 65, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Security observations 66

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 66, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

345

135

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Performance logs 67

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 67, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 68

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 68, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 69

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 69, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);

Document Conversion Field Guide

Page 15

const chunk = { file_path, chunk_index, chunk_total };

Search verification 70

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 70, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 71

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 71, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

370

145

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

WebView lifecycle 72

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 72, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 73

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 73, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Performance logs 74

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 74, included to create realistic page density and chunk boundaries. If the same

Document Conversion Field Guide

Page 16

phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 75

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 75, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 76

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 76, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Latency ms

Payload KB

Status

Value

395

155

open

Interpretation

Measured after reload

May cross a chunk boundary

Keep source label

Search verification 77

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 77, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Workbook context 78

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 78, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 79

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 79, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can

Document Conversion Field Guide

Page 17

distinguish the sources.

Security observations 80

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 80, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 81

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 81, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Metric

Value

Interpretation

Latency ms

Payload KB

420

165

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Chunk metadata 82

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 82, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Incremental indexing 83

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 83, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 84

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 84, included to create realistic page density and chunk boundaries. If the same

Document Conversion Field Guide

Page 18

phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 85

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 85, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

WebView lifecycle 86

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 86, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

445

175

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Security observations 87

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 87, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 88

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 88, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 89

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 89, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can

Document Conversion Field Guide

Page 19

distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Incremental indexing 90

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 90, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 91

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 91, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Latency ms

Payload KB

Status

Value

470

185

open

Interpretation

Measured after reload

May cross a chunk boundary

Keep source label

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Workbook context 92

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 92, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 93

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 93, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Security observations 94

Document Conversion Field Guide

Page 20

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 94, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 95

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 95, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 96

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 96, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

495

195

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Incremental indexing 97

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 97, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Search verification 98

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 98, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 99

Document Conversion Field Guide

Page 21

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 99, included to create realistic page density and chunk boundaries. If the same
phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

WebView lifecycle 100

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 100, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Security observations 101

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 101, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Metric

Value

Interpretation

Latency ms

Payload KB

520

205

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Performance logs 102

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 102, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Chunk metadata 103

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 103, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 104

Document Conversion Field Guide

Page 22

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 104, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Search verification 105

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 105, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Workbook context 106

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 106, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Latency ms

Payload KB

Status

Value

545

215

open

Interpretation

Measured after reload

May cross a chunk boundary

Keep source label

WebView lifecycle 107

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 107, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 108

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 108, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 109

Document Conversion Field Guide

Page 23

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 109, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Chunk metadata 110

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 110, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Incremental indexing 111

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 111, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

570

225

Measured after reload

May cross a chunk boundary

Status

resolved

Keep source label

Search verification 112

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 112, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 113

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 113, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);

Document Conversion Field Guide

Page 24

const chunk = { file_path, chunk_index, chunk_total };

WebView lifecycle 114

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 114, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Security observations 115

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 115, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Performance logs 116

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 116, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Metric

Value

Interpretation

Latency ms

Payload KB

595

235

Measured after reload

May cross a chunk boundary

Status

investigating

Keep source label

Chunk metadata 117

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 117, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

await webView.EnsureCoreWebView2Async(null);
webView.CoreWebView2.PostWebMessageAsString(payload);
const chunk = { file_path, chunk_index, chunk_total };

Incremental indexing 118

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 118, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Document Conversion Field Guide

Page 25

Reference: https://developer.microsoft.com/en-us/microsoft-edge/webview2/ and
https://github.com/react-native-webview/react-native-webview

Search verification 119

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 119, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Workbook context 120

A converted file should retain the relationship between a heading, a platform label, an observation, and the reference
URL that supports the observation. The source may contain blank rows, repeated headers, or a note placed far away
from the nearest table. This is field note 120, included to create realistic page density and chunk boundaries. If the
same phrase occurs in multiple files, search results should preserve the file path and chunk index so an operator can
distinguish the sources.

Document Conversion Field Guide

Page 26

