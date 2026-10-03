import json
from app.models import Department, DocType
from app.indexer.classifier import classify_file


def test_classify_file_matches(db_session):
    # Add test department & doc type
    db_session.add(Department(name="HR", path_patterns=json.dumps(["*\\hr\\*", "*\\human resources\\*"])))
    db_session.add(DocType(name="CL", path_patterns=json.dumps(["*\\cl\\*", "*circular*"])))
    db_session.commit()

    file_path = r"\\pc135\D\HR\CL\circular_2024.docx"
    res = classify_file(file_path, db_session)

    assert "HR" in res["departments"]
    assert "CL" in res["doc_types"]


def test_classify_file_no_match(db_session):
    file_path = r"\\pc135\D\RandomFolder\file.txt"
    res = classify_file(file_path, db_session)

    assert res["departments"] == []
    assert res["doc_types"] == []
