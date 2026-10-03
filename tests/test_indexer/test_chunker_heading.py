from app.indexer.chunker.heading import HeadingAwareChunker


def test_heading_aware_chunker_with_h1():
    md = """# Section One
This is section one content.

# Section Two
This is section two content.
"""
    chunker = HeadingAwareChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.chunk(md, "doc.docx")

    assert len(chunks) == 2
    assert "Section: Section One" in chunks[0].section_context
    assert "Section: Section Two" in chunks[1].section_context


def test_heading_aware_chunker_no_h1():
    md = "Plain prose document with no headings present."
    chunker = HeadingAwareChunker(chunk_size=100, chunk_overlap=10)
    chunks = chunker.chunk(md, "plain.txt")

    assert len(chunks) == 1
    assert "Document: plain.txt" in chunks[0].section_context
