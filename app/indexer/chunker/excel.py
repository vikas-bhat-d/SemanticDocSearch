import re
from typing import List
from app.indexer.chunker.base import BaseChunker, ChunkResult


class ExcelChunker(BaseChunker):
    _EMPTY_CELL_VALUES = {"", "nan", "none", "null", "nat", "<na>"}

    def __init__(self, rows_per_chunk: int = 15):
        self.rows_per_chunk = rows_per_chunk

    def chunk(self, md_text: str, file_name: str) -> List[ChunkResult]:
        if not md_text or not md_text.strip():
            return []

        # Split sheets by H2 headers "## "
        raw_sections = re.split(r'(?m)^##\s+', md_text)
        sheets = []

        if len(raw_sections) <= 1:
            # CSV or single sheet document without H2 headers
            sheet_name = file_name
            sheets.append((sheet_name, md_text))
        else:
            for section in raw_sections:
                if not section.strip():
                    continue
                lines = section.strip().split("\n", 1)
                sheet_name = lines[0].strip()
                content = lines[1] if len(lines) > 1 else ""
                sheets.append((sheet_name, content))

        results: List[ChunkResult] = []

        for sheet_name, content in sheets:
            table_rows = self._parse_markdown_table(content)
            if not table_rows:
                continue

            # Drop empty columns
            table_rows = self._clean_table(table_rows)
            if not table_rows:
                continue

            anchor_row = table_rows[0]
            data_rows = table_rows[1:]

            if not data_rows:
                # Only header row existed
                text = f"[Sheet: {sheet_name}]\n{anchor_row}"
                results.append(ChunkResult(
                    text=text,
                    chunk_index=0,
                    chunk_total=1,
                    section_context=f"Sheet: {sheet_name}"
                ))
                continue

            batches = self._batch_rows_with_overlap(data_rows, self.rows_per_chunk, overlap=2)

            for batch in batches:
                row_block = "\n".join(batch)
                text = f"[Sheet: {sheet_name}]\n{anchor_row}\n{row_block}"
                results.append(ChunkResult(
                    text=text,
                    chunk_index=len(results),
                    chunk_total=0,  # updated at end
                    section_context=f"Sheet: {sheet_name}"
                ))

        total = len(results)
        for i, r in enumerate(results):
            r.chunk_index = i
            r.chunk_total = total

        return results

    def _parse_markdown_table(self, content: str) -> List[str]:
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        table_lines = []
        for line in lines:
            if line.startswith("|") or "|" in line:
                # Skip markdown separator lines like |---|---|
                if re.match(r'^\s*\|?\s*:?-+:?\s*(\|?\s*:?-+:?\s*)*\|?\s*$', line):
                    continue
                table_lines.append(line)
        return table_lines

    def _clean_table(self, table_lines: List[str]) -> List[str]:
        # Parse into a normalized grid. MarkItDown can represent empty Excel
        # cells as literal strings such as "NaN" or "Unnamed: 3". Normalize
        # those before both embedding and payload storage so search excerpts
        # do not expose conversion artifacts.
        grid = []
        for line in table_lines:
            cells = [self._normalize_cell(c) for c in line.strip("|").split("|")]
            if any(c for c in cells):
                grid.append(cells)

        if not grid:
            return []

        # Find columns that have at least one non-empty value
        max_cols = max(len(cells) for cells in grid)
        col_has_val = [False] * max_cols
        for cells in grid:
            for i, c in enumerate(cells):
                if c:
                    col_has_val[i] = True

        cleaned_lines = []
        for cells in grid:
            filtered_cells = [cells[i] if i < len(cells) else "" for i in range(max_cols) if col_has_val[i]]
            cleaned_lines.append("| " + " | ".join(filtered_cells) + " |")

        return cleaned_lines

    def _normalize_cell(self, cell: str) -> str:
        value = cell.strip()
        if value.lower() in self._EMPTY_CELL_VALUES:
            return ""
        if re.fullmatch(r"unnamed\s*:\s*\d+", value, flags=re.IGNORECASE):
            return ""
        return value

    def _batch_rows_with_overlap(self, rows: List[str], batch_size: int, overlap: int) -> List[List[str]]:
        batches = []
        i = 0
        while i < len(rows):
            batch = rows[i:i + batch_size]
            batches.append(batch)
            if i + batch_size >= len(rows):
                break
            i += (batch_size - overlap)
        return batches
