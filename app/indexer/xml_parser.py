import os
import re
import xml.etree.ElementTree as ET
from typing import List, Tuple


def convert_backup_path(backup_path: str) -> str:
    """
    Finds the segment matching pattern MACHINENAME(DRIVELETTER.)
    e.g. PC135(D.) → machine=pc135, drive=D
    Everything after that segment becomes the UNC path.
    """
    pattern = re.compile(r'([A-Za-z0-9_-]+)\(([A-Za-z])\.\)')
    parts = backup_path.replace('/', '\\').split('\\')

    for i, part in enumerate(parts):
        match = pattern.fullmatch(part)
        if match:
            machine = match.group(1).lower()
            drive = match.group(2).upper()
            rest = '\\'.join(parts[i + 1:])
            if rest:
                return f"\\\\{machine}\\{drive}\\{rest}"
            return f"\\\\{machine}\\{drive}"

    return backup_path


def parse_incremental_xml(xml_path_or_content: str) -> List[Tuple[str, str]]:
    """
    Parses an incremental XML file or string and returns a list of (type, converted_path) tuples.
    Type is either 'FILE' or 'FOLDER'.
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

            if val_str:
                converted = convert_backup_path(val_str)
                results.append((type_str, converted))

    return results
