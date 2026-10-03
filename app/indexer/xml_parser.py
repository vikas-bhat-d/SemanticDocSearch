import os
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple


def convert_backup_path(backup_path: str) -> str:
    r"""
    Converts legacy backup paths containing a MACHINENAME(DRIVELETTER.)
    segment to UNC, while preserving direct local and UNC paths.

    Examples:
      PC135(D.)\Desktop\file.xlsx → \\pc135\D\Desktop\file.xlsx
      C:\Projects\SampleFolders\04_office → C:\Projects\SampleFolders\04_office
    """
    pattern = re.compile(r'([A-Za-z0-9_-]+)\(([A-Za-z])\.\)')
    normalized_path = backup_path.replace('/', '\\')
    parts = normalized_path.split('\\')

    for i, part in enumerate(parts):
        match = pattern.fullmatch(part)
        if match:
            machine = match.group(1).lower()
            drive = match.group(2).upper()
            rest = '\\'.join(parts[i + 1:])
            if rest:
                return f"\\\\{machine}\\{drive}\\{rest}"
            return f"\\\\{machine}\\{drive}"

    # Direct local paths and existing UNC paths do not need conversion.
    return normalized_path


def parse_incremental_xml(xml_path_or_content: str) -> List[Tuple[str, str]]:
    """
    Parses an incremental XML file or string and returns file entries as
    ``(type, converted_path)`` tuples.

    Incremental processing is intentionally file-only. Entries with any other
    type, including ``FOLDER``, are ignored so a folder-level XML entry cannot
    trigger a full-folder delete or reindex.
    """
    results = []

    if not xml_path_or_content or not xml_path_or_content.strip():
        return results

    content = xml_path_or_content.strip()
    if os.path.exists(content):
        with open(content, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return results

    for item in root.findall(".//FILELIST"):
        type_elem = item.find("Type")
        val_elem = item.find("Value")

        if type_elem is not None and val_elem is not None:
            type_str = (type_elem.text or "").strip().upper()
            val_str = (val_elem.text or "").strip()

            if type_str != "FILE" or not val_str:
                continue

            converted = convert_backup_path(val_str)
            results.append(("FILE", converted))

    return results
