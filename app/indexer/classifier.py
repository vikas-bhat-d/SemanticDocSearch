import json
import fnmatch
from typing import Dict, List
from sqlalchemy.orm import Session
from app.models import Department, DocType


def classify_file(file_path: str, db: Session) -> Dict[str, List[str]]:
    departments = []
    doc_types = []

    path_normalized = file_path.replace('/', '\\').lower()

    dept_rows = db.query(Department).all()
    for dept in dept_rows:
        try:
            patterns = json.loads(dept.path_patterns) if isinstance(dept.path_patterns, str) else dept.path_patterns
            for pattern in patterns:
                pat_norm = pattern.replace('/', '\\').lower()
                if fnmatch.fnmatch(path_normalized, pat_norm):
                    departments.append(dept.name)
                    break
        except Exception:
            continue

    dt_rows = db.query(DocType).all()
    for dt in dt_rows:
        try:
            patterns = json.loads(dt.path_patterns) if isinstance(dt.path_patterns, str) else dt.path_patterns
            for pattern in patterns:
                pat_norm = pattern.replace('/', '\\').lower()
                if fnmatch.fnmatch(path_normalized, pat_norm):
                    doc_types.append(dt.name)
                    break
        except Exception:
            continue

    return {"departments": departments, "doc_types": doc_types}
