import re
from typing import Iterator, List, Optional, Tuple

from app.indexer.chunker.base import BaseChunker, ChunkResult


class ExcelChunker(BaseChunker):
    _EMPTY_CELL_VALUES = {"", "nan", "none", "null", "nat", "<na>"}

    def __init__(self, rows_per_chunk: int = 15):
        self.rows_per_chunk = max(1, rows_per_chunk)

    def _sheets(self, md_text: str, file_name: str) -> Iterator[Tuple[str, str]]:
        pattern = re.compile(r"(?ms)^##\s+([^\n]*)\n?(.*?)(?=^##\s+|\Z)")
        found = False
        for match in pattern.finditer(md_text):
            found = True
            yield match.group(1).strip(), match.group(2)
        if not found:
            yield file_name, md_text

    def iter_chunks(
        self,
        md_text: str,
        file_name: str,
        max_chunk_chars: Optional[int] = None,
    ) -> Iterator[ChunkResult]:
        if not md_text or not md_text.strip():
            return

        chunk_index = 0
        for sheet_name, content in self._sheets(md_text, file_name):
            table_rows = self._clean_table(self._parse_markdown_table(content))
            if not table_rows:
                continue
            anchor_row = table_rows[0]
            data_rows = table_rows[1:]
            batches = self._iter_batches(data_rows, self.rows_per_chunk, overlap=2)
            if not data_rows:
                batches = iter(([],))
            for batch in batches:
                row_block = "\n".join(batch)
                text = f"[Sheet: {sheet_name}]\n{anchor_row}"
                if row_block:
                    text += f"\n{row_block}"
                if max_chunk_chars and len(text) > max_chunk_chars:
                    raise ValueError(
                        f"Chunk {chunk_index} exceeds max_chunk_chars ({max_chunk_chars})"
                    )
                yield ChunkResult(
                    text=text,
                    chunk_index=chunk_index,
                    chunk_total=0,
                    section_context=f"Sheet: {sheet_name}",
                )
                chunk_index += 1

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        results = list(self.iter_chunks(md_text, file_name))
        total = len(results)
        for index, result in enumerate(results):
            result.chunk_index = index
            result.chunk_total = total
        return results

    def _parse_markdown_table(self, content: str) -> List[str]:
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        table_lines = []
        for line in lines:
            if line.startswith("|") or "|" in line:
                if re.match(r'^\s*\|?\s*:?-+:?\s*(\|?\s*:?-+:?\s*)*\|?\s*$', line):
                    continue
                table_lines.append(line)
        return table_lines

    def _clean_table(self, table_lines: List[str]) -> List[str]:
        grid = []
        for line in table_lines:
            cells = [self._normalize_cell(c) for c in line.strip("|").split("|")]
            if any(c for c in cells):
                grid.append(cells)
        if not grid:
            return []

        max_cols = max(len(cells) for cells in grid)
        col_has_val = [False] * max_cols
        for cells in grid:
            for index, cell in enumerate(cells):
                if cell:
                    col_has_val[index] = True

        cleaned_lines = []
        for cells in grid:
            filtered = [
                cells[index] if index < len(cells) else ""
                for index in range(max_cols)
                if col_has_val[index]
            ]
            cleaned_lines.append("| " + " | ".join(filtered) + " |")
        return cleaned_lines

    def _normalize_cell(self, cell: str) -> str:
        value = cell.strip()
        if value.lower() in self._EMPTY_CELL_VALUES:
            return ""
        if re.fullmatch(r"unnamed\s*:\s*\d+", value, flags=re.IGNORECASE):
            return ""
        return value

    def _iter_batches(self, rows: List[str], batch_size: int, overlap: int) -> Iterator[List[str]]:
        index = 0
        step = max(1, batch_size - overlap)
        while index < len(rows):
            batch = rows[index:index + batch_size]
            yield batch
            if index + batch_size >= len(rows):
                break
            index += step
