from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.indexer.chunker.base import BaseChunker, ChunkResult


class GenericChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        if not md_text or not md_text.strip():
            return []

        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=lambda txt: len(txt.split())
        )

        sub_texts = splitter.split_text(md_text.strip())
        total = len(sub_texts)

        results = []
        for idx, txt in enumerate(sub_texts):
            results.append(ChunkResult(
                text=txt,
                chunk_index=idx,
                chunk_total=total,
                section_context=""
            ))

        return results
