from app.indexer.chunker.generic import GenericChunker


def test_generic_chunker():
    md = "Paragraph one text.\n\nParagraph two text.\n\nParagraph three text."
    chunker = GenericChunker(chunk_size=10, chunk_overlap=2)
    chunks = chunker.chunk(md, "file.pdf")

    assert len(chunks) >= 1
    assert chunks[0].section_context == ""
