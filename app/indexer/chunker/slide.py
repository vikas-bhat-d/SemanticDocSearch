import re
from typing import Iterator, List, Optional, Tuple

from app.indexer.chunker.base import BaseChunker, ChunkResult


class SlideChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512):
        self.chunk_size = chunk_size

    def _slides(self, md_text: str) -> Iterator[Tuple[int, str, int]]:
        marker = re.compile(r"<!--\s*Slide number:\s*(\d+)\s*-->")
        total_slides = sum(1 for _ in marker.finditer(md_text))
        if not total_slides:
            yield 1, md_text.strip(), 1
            return
        matches = marker.finditer(md_text)
        current = next(matches)
        for next_match in matches:
            yield int(current.group(1)), md_text[current.end():next_match.start()].strip(), total_slides
            current = next_match
        yield int(current.group(1)), md_text[current.end():].strip(), total_slides

    def iter_chunks(
        self,
        md_text: str,
        file_name: str,
        max_chunk_chars: Optional[int] = None,
    ) -> Iterator[ChunkResult]:
        if not md_text or not md_text.strip():
            return

        chunk_index = 0
        for slide_num, content, total_slides in self._slides(md_text):
            if not content:
                continue
            context = f"Slide {slide_num}"
            prefix = f"[Slide {slide_num} of {total_slides}]"
            if len(content.split()) <= self.chunk_size:
                text = f"{prefix}\n{content}"
                if max_chunk_chars and len(text) > max_chunk_chars:
                    raise ValueError(
                        f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                    )
                yield ChunkResult(text, chunk_index, 0, context)
                chunk_index += 1
                continue

            current: List[str] = []
            tokens = 0
            for sentence in re.split(r"(?<=\.)\s+", content):
                sentence_tokens = len(sentence.split())
                if current and tokens + sentence_tokens > self.chunk_size:
                    text = f"{prefix}\n{' '.join(current)}"
                    if max_chunk_chars and len(text) > max_chunk_chars:
                        raise ValueError(
                            f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                        )
                    yield ChunkResult(text, chunk_index, 0, context)
                    chunk_index += 1
                    current = []
                    tokens = 0
                current.append(sentence)
                tokens += sentence_tokens
            if current:
                text = f"{prefix}\n{' '.join(current)}"
                if max_chunk_chars and len(text) > max_chunk_chars:
                    raise ValueError(
                        f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                    )
                yield ChunkResult(text, chunk_index, 0, context)
                chunk_index += 1

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        results = list(self.iter_chunks(md_text, file_name))
        total = len(results)
        for index, result in enumerate(results):
            result.chunk_index = index
            result.chunk_total = total
        return results
