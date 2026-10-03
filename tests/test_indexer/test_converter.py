import pytest
from app.indexer.converter import DocumentConverter


def test_converter_missing_file():
    converter = DocumentConverter()
    with pytest.raises(FileNotFoundError):
        converter.convert("non_existent_file_path_12345.docx")
