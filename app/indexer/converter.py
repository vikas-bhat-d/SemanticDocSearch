import os
import queue
import threading
from typing import Optional

from markitdown import MarkItDown, UnsupportedFormatException


class EmptyContentError(ValueError):
    """Raised when a file has no content that can be indexed."""


class FileSizeLimitError(ValueError):
    """Raised when a file exceeds the configured source-size limit."""


class UnsupportedFileTypeError(ValueError):
    """Raised when MarkItDown has no converter for a file type."""


class DocumentConverter:
    """Per-worker MarkItDown wrapper with source/output/time guards."""

    def __init__(
        self,
        max_file_size_mb: int = 100,
        max_markdown_chars: Optional[int] = 10_000_000,
        conversion_timeout_seconds: Optional[float] = 300.0,
    ):
        self.max_file_size_mb = max_file_size_mb
        self.max_markdown_chars = max_markdown_chars
        self.conversion_timeout_seconds = conversion_timeout_seconds
        self.md_converter = MarkItDown()

    def _convert_with_markitdown(self, file_path: str, result_queue: queue.Queue):
        try:
            result = self.md_converter.convert(file_path)
            result_queue.put((True, result.text_content if hasattr(result, "text_content") else str(result)))
        except Exception as exc:  # pragma: no cover - exercised through convert
            result_queue.put((False, exc))

    def convert(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if os.path.getsize(file_path) == 0:
            raise EmptyContentError("File is empty")

        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            raise FileSizeLimitError(
                f"File size ({file_size_mb:.2f} MB) exceeds maximum limit of "
                f"{self.max_file_size_mb} MB"
            )

        result_queue: queue.Queue = queue.Queue(maxsize=1)
        conversion_thread = threading.Thread(
            target=self._convert_with_markitdown,
            args=(file_path, result_queue),
            daemon=True,
        )
        conversion_thread.start()
        timeout = self.conversion_timeout_seconds
        conversion_thread.join(timeout=timeout if timeout and timeout > 0 else None)
        if conversion_thread.is_alive():
            raise TimeoutError(
                f"MarkItDown conversion exceeded {self.conversion_timeout_seconds} seconds"
            )

        succeeded, value = result_queue.get()
        if not succeeded:
            if isinstance(value, UnsupportedFormatException):
                raise UnsupportedFileTypeError(str(value)) from value
            raise RuntimeError(f"MarkItDown conversion failed: {value}")
        md_text = value
        if not md_text or not md_text.strip():
            raise EmptyContentError("File produced empty or whitespace-only markdown content")
        if self.max_markdown_chars and len(md_text) > self.max_markdown_chars:
            raise ValueError(
                f"Expanded markdown ({len(md_text)} characters) exceeds maximum limit of "
                f"{self.max_markdown_chars} characters"
            )
        return md_text
