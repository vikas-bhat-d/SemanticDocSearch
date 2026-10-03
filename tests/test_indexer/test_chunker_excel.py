from app.indexer.chunker.excel import ExcelChunker


def test_excel_chunker_sheets():
    md = """## Sheet1
| Col1 | Col2 |
|---|---|
| Val1 | Val2 |
| Val3 | Val4 |

## Sheet2
| ColA | ColB |
|---|---|
| A1 | B1 |
"""
    chunker = ExcelChunker(rows_per_chunk=10)
    chunks = chunker.chunk(md, "test.xlsx")

    assert len(chunks) == 2
    assert "Sheet: Sheet1" in chunks[0].section_context
    assert "Sheet: Sheet2" in chunks[1].section_context
    assert "[Sheet: Sheet1]" in chunks[0].text
    assert "Val1" in chunks[0].text


def test_excel_chunker_csv_fallback():
    csv_md = """| Name | Age |
|---|---|
| Alice | 30 |
| Bob | 25 |
"""
    chunker = ExcelChunker(rows_per_chunk=10)
    chunks = chunker.chunk(csv_md, "data.csv")

    assert len(chunks) == 1
    assert "data.csv" in chunks[0].section_context
    assert "Alice" in chunks[0].text
