import re
from typing import Iterator, List, Optional

from app.indexer.chunker.base import BaseChunker, ChunkResult


class GenericChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = min(max(0, chunk_overlap), max(0, chunk_size - 1))

    def iter_chunks(
        self,
        md_text: str,
        file_name: str,
        max_chunk_chars: Optional[int] = None,
    ) -> Iterator[ChunkResult]:
        if not md_text or not md_text.strip():
            return

        # Consume words incrementally.  Only the current chunk and its
        # overlap remain live; no document-sized list of split chunks is made.
        current: List[str] = []
        chunk_index = 0
        new_words = 0
        for match in re.finditer(r"\S+", md_text.strip()):
            current.append(match.group(0))
            new_words += 1
            if len(current) >= self.chunk_size:
                text = " ".join(current)
                if max_chunk_chars and len(text) > max_chunk_chars:
                    raise ValueError(
                        f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                    )
                yield ChunkResult(text, chunk_index, 0, "")
                chunk_index += 1
                current = current[-self.chunk_overlap:] if self.chunk_overlap else []
                new_words = 0

        if current and new_words:
            text = " ".join(current)
            if max_chunk_chars and len(text) > max_chunk_chars:
                raise ValueError(
                    f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                )
            yield ChunkResult(text, chunk_index, 0, "")

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        results = list(self.iter_chunks(md_text, file_name))
        total = len(results)
        for index, result in enumerate(results):
            result.chunk_index = index
            result.chunk_total = total
        return results
