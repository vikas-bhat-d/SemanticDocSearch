from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Iterator, List, Optional


@dataclass
class ChunkResult:
    text: str              # full text to embed (includes context prefix)
    chunk_index: int       # 0-based index
    chunk_total: int       # filled after all chunks produced
    section_context: str   # "Sheet: RN_WebView" / "Section: React Native" / "Slide 3"


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        pass

    def iter_chunks(self, md_text: str, file_name: str, max_chunk_chars: Optional[int] = None) -> Iterator[ChunkResult]:
        """Streaming-compatible interface retained for existing chunkers.

        Format-specific chunkers can override this to parse one section at a
        time.  The default keeps compatibility with third-party chunkers that
        only implement ``chunk``.
        """
        for chunk in self.chunk(md_text, file_name):
            if max_chunk_chars and len(chunk.text) > max_chunk_chars:
                raise ValueError(
                    f"Chunk {chunk.chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                )
            yield chunk

    def iter_chunk_batches(
        self,
        md_text: str,
        file_name: str,
        batch_size: int,
        max_chunk_chars: Optional[int] = None,
    ) -> Iterator[List[ChunkResult]]:
        """Yield at most ``batch_size`` chunks and release each batch promptly."""
        if batch_size < 1:
            raise ValueError("Chunk batch size must be positive")
        batch: List[ChunkResult] = []
        for chunk in self.iter_chunks(md_text, file_name, max_chunk_chars=max_chunk_chars):
            batch.append(chunk)
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch
