import json
from app.models import Synonym
from app.search.synonyms import expand_query


def test_synonym_expansion(db_session):
    db_session.add(Synonym(term="workstation", synonyms=json.dumps(["laptop", "desktop", "pc"])))
    db_session.commit()

    expanded, syns_used = expand_query("my workstation", db_session)
    assert "laptop" in expanded
    assert "desktop" in expanded
    assert "laptop" in syns_used
