import re
from typing import Iterator, List, Optional, Tuple

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.indexer.chunker.base import BaseChunker, ChunkResult


class HeadingAwareChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=lambda txt: len(txt.split()),
        )

    def _sections(self, md_text: str, file_name: str) -> Iterator[Tuple[str, str]]:
        pattern = re.compile(r"(?ms)^#\s+([^\n]*)\n?(.*?)(?=^#\s+|\Z)")
        first_start = None
        found = False
        for match in pattern.finditer(md_text):
            found = True
            if first_start is None:
                first_start = match.start()
                preamble = md_text[:first_start].strip()
                if preamble:
                    yield f"Document: {file_name}", preamble
            heading = match.group(1).strip()
            body = match.group(2).strip()
            if body:
                yield f"Section: {heading}", f"# {heading}\n{body}"
        if not found:
            yield f"Document: {file_name}", md_text.strip()

    def iter_chunks(
        self,
        md_text: str,
        file_name: str,
        max_chunk_chars: Optional[int] = None,
    ) -> Iterator[ChunkResult]:
        if not md_text or not md_text.strip():
            return

        chunk_index = 0
        for heading_context, content in self._sections(md_text, file_name):
            if len(content.split()) <= self.chunk_size:
                text = f"[{heading_context}]\n{content}"
                if max_chunk_chars and len(text) > max_chunk_chars:
                    raise ValueError(
                        f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                    )
                yield ChunkResult(text, chunk_index, 0, heading_context)
                chunk_index += 1
                continue

            for block in self._split_preserving_blocks(content):
                block_parts = (
                    [block]
                    if len(block.split()) <= self.chunk_size
                    else self._splitter.split_text(block)
                )
                for part in block_parts:
                    text = f"[{heading_context}]\n{part}"
                    if max_chunk_chars and len(text) > max_chunk_chars:
                        raise ValueError(
                            f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                        )
                    yield ChunkResult(text, chunk_index, 0, heading_context)
                    chunk_index += 1

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        results = list(self.iter_chunks(md_text, file_name))
        total = len(results)
        for index, result in enumerate(results):
            result.chunk_index = index
            result.chunk_total = total
        return results

    def _split_preserving_blocks(self, text: str) -> List[str]:
        pattern = r"(```[\s\S]*?```|\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)*)"
        return [part.strip() for part in re.split(pattern, text) if part and part.strip()]
