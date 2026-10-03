import json
import re
from typing import Tuple, List
from sqlalchemy.orm import Session
from app.models import Synonym


def expand_query(query: str, db: Session) -> Tuple[str, List[str]]:
    if not query or not query.strip():
        return query, []

    words = [w.lower() for w in re.findall(r'\b\w+\b', query)]
    if not words:
        return query, []

    synonyms_used = set()
    expanded_words = list(words)

    syn_rows = db.query(Synonym).all()
    syn_map = {}
    for r in syn_rows:
        try:
            syn_list = json.loads(r.synonyms) if isinstance(r.synonyms, str) else r.synonyms
            syn_map[r.term.lower()] = [s.lower() for s in syn_list]
        except Exception:
            continue

    for w in words:
        if w in syn_map:
            for syn in syn_map[w]:
                if syn not in expanded_words:
                    expanded_words.append(syn)
                    synonyms_used.add(syn)

    expanded_query = " ".join(expanded_words)
    return expanded_query, sorted(list(synonyms_used))
