import re
from typing import List
from app.indexer.chunker.base import BaseChunker, ChunkResult


class SlideChunker(BaseChunker):
    def __init__(self, chunk_size: int = 512):
        self.chunk_size = chunk_size

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        if not md_text or not md_text.strip():
            return []

        # Split on <!-- Slide number: N --> markers
        slide_pattern = r'<!--\s*Slide number:\s*(\d+)\s*-->'
        raw_parts = re.split(slide_pattern, md_text)

        slides = []
        if len(raw_parts) <= 1:
            # Fallback if no slide markers present
            slides.append((1, md_text.strip()))
        else:
            # raw_parts[0] is preamble before slide 1
            i = 1
            while i < len(raw_parts):
                slide_num = int(raw_parts[i])
                slide_content = raw_parts[i + 1].strip() if i + 1 < len(raw_parts) else ""
                slides.append((slide_num, slide_content))
                i += 2

        total_slides = len(slides)
        results: List[ChunkResult] = []

        for slide_num, content in slides:
            if not content:
                continue

            sec_context = f"Slide {slide_num}"
            prefix = f"[Slide {slide_num} of {total_slides}]"
            token_count = len(content.split())

            if token_count <= self.chunk_size:
                text = f"{prefix}\n{content}"
                results.append(ChunkResult(
                    text=text,
                    chunk_index=0,
                    chunk_total=0,
                    section_context=sec_context
                ))
            else:
                # Split large slide on sentence boundaries (". ")
                sentences = re.split(r'(?<=\.)\s+', content)
                curr_sentences = []
                curr_tokens = 0

                for s in sentences:
                    s_tok = len(s.split())
                    if curr_tokens + s_tok > self.chunk_size and curr_sentences:
                        part_text = " ".join(curr_sentences)
                        results.append(ChunkResult(
                            text=f"{prefix}\n{part_text}",
                            chunk_index=0,
                            chunk_total=0,
                            section_context=sec_context
                        ))
                        curr_sentences = [s]
                        curr_tokens = s_tok
                    else:
                        curr_sentences.append(s)
                        curr_tokens += s_tok

                if curr_sentences:
                    part_text = " ".join(curr_sentences)
                    results.append(ChunkResult(
                        text=f"{prefix}\n{part_text}",
                        chunk_index=0,
                        chunk_total=0,
                        section_context=sec_context
                    ))

        total = len(results)
        for idx, r in enumerate(results):
            r.chunk_index = idx
            r.chunk_total = total

        return results
