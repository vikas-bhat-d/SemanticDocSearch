from types import SimpleNamespace
from unittest.mock import Mock

from markitdown import UnsupportedFormatException
import pytest
from app.indexer.converter import (
    DocumentConverter,
    EmptyContentError,
    FileSizeLimitError,
    UnsupportedFileTypeError,
)


def test_converter_missing_file():
    converter = DocumentConverter()
    with pytest.raises(FileNotFoundError):
        converter.convert("non_existent_file_path_12345.docx")


def test_converter_rejects_empty_file_before_markitdown(monkeypatch, tmp_path):
    file_path = tmp_path / "empty.md"
    file_path.write_bytes(b"")
    converter = DocumentConverter()
    markitdown_convert = Mock()
    monkeypatch.setattr(converter.md_converter, "convert", markitdown_convert)

    with pytest.raises(EmptyContentError, match="File is empty"):
        converter.convert(str(file_path))

    markitdown_convert.assert_not_called()


def test_converter_rejects_empty_markdown_output(monkeypatch, tmp_path):
    file_path = tmp_path / "no-text.md"
    file_path.write_text("source exists", encoding="utf-8")
    converter = DocumentConverter()

    def fake_convert(path):
        return SimpleNamespace(text_content=" \n", source_path=path)

    monkeypatch.setattr(
        converter.md_converter,
        "convert",
        fake_convert,
    )

    with pytest.raises(EmptyContentError, match="empty or whitespace-only"):
        converter.convert(str(file_path))


def test_converter_rejects_file_above_size_limit(tmp_path):
    file_path = tmp_path / "large.md"
    file_path.write_bytes(b"x" * (1024 * 1024 + 1))

    with pytest.raises(FileSizeLimitError, match="exceeds maximum limit"):
        DocumentConverter(max_file_size_mb=1).convert(str(file_path))


def test_converter_translates_markitdown_unsupported_format(monkeypatch, tmp_path):
    file_path = tmp_path / "legacy.doc"
    file_path.write_text("legacy document", encoding="utf-8")
    converter = DocumentConverter()
    monkeypatch.setattr(
        converter.md_converter,
        "convert",
        Mock(side_effect=UnsupportedFormatException("no converter")),
    )

    with pytest.raises(UnsupportedFileTypeError, match="no converter"):
        converter.convert(str(file_path))
