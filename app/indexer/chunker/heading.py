import re
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.indexer.chunker.base import BaseChunker, ChunkResult


class HeadingAwareChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        if not md_text or not md_text.strip():
            return []

        # Split on H1 headings (lines starting with "# ")
        # Match H1 pattern at start of line
        raw_sections = re.split(r'(?m)^#\s+', md_text)
        sections = []

        if len(raw_sections) <= 1:
            # No H1 headings present
            sections.append((f"Document: {file_name}", md_text.strip()))
        else:
            first = raw_sections[0].strip()
            if first:
                sections.append((f"Document: {file_name}", first))

            for sec in raw_sections[1:]:
                if not sec.strip():
                    continue
                lines = sec.strip().split("\n", 1)
                heading = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                sections.append((f"Section: {heading}", f"# {heading}\n{body}"))

        results: List[ChunkResult] = []
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=lambda txt: len(txt.split())  # token estimate by word count
        )

        for heading_ctx, content in sections:
            token_count = len(content.split())

            if token_count <= self.chunk_size:
                text = f"[{heading_ctx}]\n{content}"
                results.append(ChunkResult(
                    text=text,
                    chunk_index=0,
                    chunk_total=0,
                    section_context=heading_ctx
                ))
            else:
                # Protect tables and code blocks if possible
                blocks = self._split_preserving_blocks(content)
                sub_chunks = []
                for b in blocks:
                    b_tokens = len(b.split())
                    if b_tokens <= self.chunk_size:
                        sub_chunks.append(b)
                    else:
                        sub_chunks.extend(splitter.split_text(b))

                for sc in sub_chunks:
                    text = f"[{heading_ctx}]\n{sc}"
                    results.append(ChunkResult(
                        text=text,
                        chunk_index=0,
                        chunk_total=0,
                        section_context=heading_ctx
                    ))

        total = len(results)
        for i, r in enumerate(results):
            r.chunk_index = i
            r.chunk_total = total

        return results

    def _split_preserving_blocks(self, text: str) -> List[str]:
        """
        Splits text into blocks, preserving tables and ```code blocks intact.
        """
        pattern = r'(```[\s\S]*?```|\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)*)'
        parts = re.split(pattern, text)
        blocks = []
        for p in parts:
            if p and p.strip():
                blocks.append(p.strip())
        return blocks
