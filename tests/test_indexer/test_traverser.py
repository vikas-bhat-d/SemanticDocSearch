from app.models import IndexFolder, ExcludedPath, FileTypeConfig
from app.indexer.traverser import (
    get_index_roots,
    walk_folders,
    is_path_excluded,
    is_ext_excluded,
)


def test_is_path_excluded():
    exclusions = [r"C:\Temp", r"*\ExcludedFolder\*"]
    assert is_path_excluded(r"C:\Temp\file.txt", exclusions) is True
    assert is_path_excluded(r"C:\Docs\file.txt", exclusions) is False


def test_is_ext_excluded():
    exclusions = [".tmp", ".log"]
    assert is_ext_excluded(".tmp", exclusions) is True
    assert is_ext_excluded("tmp", exclusions) is True
    assert is_ext_excluded(".docx", exclusions) is False


def test_walk_folders_empty(db_session):
    items = list(walk_folders(db_session))
    assert items == []


def test_get_index_roots_returns_all_containing_configured_folders(db_session):
    db_session.add_all([
        IndexFolder(path=r"C:\Docs", status="completed"),
        IndexFolder(path=r"C:\Docs\Team", status="completed"),
        IndexFolder(path=r"C:\Docs2", status="completed"),
    ])
    db_session.commit()

    assert get_index_roots(db_session, r"C:\Docs\Team\policy.pdf") == [
        r"C:\Docs",
        r"C:\Docs\Team",
    ]
