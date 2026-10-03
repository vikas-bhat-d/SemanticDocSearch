import os
from typing import Optional
from markitdown import MarkItDown


class DocumentConverter:
    def __init__(self, max_file_size_mb: int = 100):
        self.max_file_size_mb = max_file_size_mb
        self.md_converter = MarkItDown()

    def convert(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise ValueError(f"File size ({file_size_mb:.2f} MB) exceeds maximum limit of {self.max_file_size_mb} MB")

        ext = os.path.splitext(file_path)[1].lower()

        try:
            result = self.md_converter.convert(file_path)
            md_text = result.text_content if hasattr(result, "text_content") else str(result)
        except Exception as e:
            raise RuntimeError(f"MarkItDown conversion failed: {str(e)}")

        if not md_text or not md_text.strip():
            raise ValueError("File produced empty or whitespace-only markdown content")

        return md_text
