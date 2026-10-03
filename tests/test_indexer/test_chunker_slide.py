from app.indexer.chunker.slide import SlideChunker


def test_slide_chunker():
    md = """<!-- Slide number: 1 -->
Slide 1 title and body.

<!-- Slide number: 2 -->
Slide 2 title and body with notes.
### Notes:
Presenter notes here.
"""
    chunker = SlideChunker(chunk_size=100)
    chunks = chunker.chunk(md, "presentation.pptx")

    assert len(chunks) == 2
    assert chunks[0].section_context == "Slide 1"
    assert chunks[1].section_context == "Slide 2"
    assert "[Slide 1 of 2]" in chunks[0].text
    assert "Presenter notes here" in chunks[1].text
