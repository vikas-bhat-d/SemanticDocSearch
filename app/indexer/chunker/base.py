from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


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
