"""Path normalization shared by filesystem discovery and incremental XML."""

import ntpath
import os
import re


_WINDOWS_PATH_RE = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\)")


def normalize_file_path(path: str) -> str:
    """Return the path representation used for filesystem/Qdrant payloads."""
    if not path:
        return path
    # ntpath also normalizes Windows paths when tests run on a non-Windows host.
    if os.name == "nt" or _WINDOWS_PATH_RE.match(path):
        return ntpath.normpath(path.replace("/", "\\"))
    return os.path.normpath(path)


def canonical_file_path(path: str) -> str:
    """Return a stable comparison key (case-insensitive on Windows paths)."""
    normalized = normalize_file_path(path)
    if os.name == "nt" or _WINDOWS_PATH_RE.match(normalized):
        return normalized.lower()
    return os.path.normcase(normalized)


def path_is_within(path: str, root: str) -> bool:
    """Safely determine whether *path* is rooted below *root*."""
    path_key = canonical_file_path(path)
    root_key = canonical_file_path(root)
    try:
        common = ntpath.commonpath([path_key, root_key]) if (
            _WINDOWS_PATH_RE.match(path_key) or _WINDOWS_PATH_RE.match(root_key)
        ) else os.path.commonpath([path_key, root_key])
    except ValueError:
        return False
    return common == root_key
