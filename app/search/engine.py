import re
import html
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import get_config
from app.indexer.embedder import Embedder
from app.indexer.qdrant_ops import get_qdrant_client, search_qdrant
from app.search.synonyms import expand_query


class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.config = get_config(db)
        self.qdrant = get_qdrant_client(host=self.config.qdrant_host, port=self.config.qdrant_port)
        self.embedder = Embedder(
            model_name=self.config.embedding_model,
            dimensions=self.config.embedding_dimensions
        )

    def search(
        self,
        query: str,
        departments: Optional[List[str]] = None,
        doc_types: Optional[List[str]] = None,
        extensions: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 10,
        exact: bool = False
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            return {
                "results": [],
                "total_files": 0,
                "total_pages": 0,
                "page": page,
                "per_page": per_page,
                "query": query,
                "synonyms_used": [],
                "exact_mode": exact
            }

        raw_q = query.strip()
        exact_phrase = None
        exact_mode = exact

        # Check quotes
        quote_match = re.search(r'"([^"]+)"', raw_q)
        if quote_match:
            exact_phrase = quote_match.group(1).lower()
            exact_mode = True
        elif exact:
            exact_phrase = raw_q.lower()

        synonyms_used = []
        if exact_mode:
            search_text = raw_q.replace('"', '')
        else:
            search_text, synonyms_used = expand_query(raw_q, self.db)

        # 2. Embed query
        query_vectors = self.embedder.embed_batch([search_text])
        if not query_vectors:
            return {
                "results": [],
                "total_files": 0,
                "total_pages": 0,
                "page": page,
                "per_page": per_page,
                "query": query,
                "synonyms_used": [],
                "exact_mode": exact_mode
            }
        query_vec = query_vectors[0]

        # 3. Vector search
        top_k = self.config.search_top_k
        raw_results = search_qdrant(
            client=self.qdrant,
            collection_name=self.config.collection_name,
            query_vector=query_vec,
            top_k=top_k,
            departments=departments,
            doc_types=doc_types,
            extensions=extensions
        )

        # 4. Group by file
        files_map: Dict[str, List[Dict[str, Any]]] = {}
        for r in raw_results:
            payload = r.payload or {}
            fp = payload.get("file_path", "")
            if not fp:
                continue

            content = payload.get("content", "")
            score = float(r.score) if hasattr(r, "score") else 0.0

            # Step 6: Exact phrase check / filter
            if exact_phrase:
                if exact_phrase not in content.lower():
                    if exact:
                        # Strictly filter out non-matching chunks in exact mode
                        continue
                else:
                    score += 0.2  # Exact match boost

            if fp not in files_map:
                files_map[fp] = []

            files_map[fp].append({
                "score": score,
                "chunk_index": payload.get("chunk_index", 0),
                "section_context": payload.get("section_context", ""),
                "content": content,
                "file_name": payload.get("file_name", ""),
                "file_extension": payload.get("file_extension", ""),
                "departments": payload.get("departments", []),
                "doc_types": payload.get("doc_types", [])
            })

        # 5. Score & rank files
        scored_files = []
        terms_to_highlight = [raw_q.replace('"', '').lower()] + [s.lower() for s in synonyms_used]

        for fp, chunks in files_map.items():
            if not chunks:
                continue
            # Sort chunks by score descending
            chunks.sort(key=lambda c: c["score"], reverse=True)
            file_score = chunks[0]["score"]

            excerpts = []
            for c in chunks[:self.config.search_excerpt_count]:
                highlighted_text = self._highlight_text(c["content"], terms_to_highlight)
                excerpts.append({
                    "text": highlighted_text,
                    "chunk_index": c["chunk_index"],
                    "section_context": c["section_context"]
                })

            sample_chunk = chunks[0]
            scored_files.append({
                "file_name": sample_chunk["file_name"],
                "file_path": fp,
                "file_extension": sample_chunk["file_extension"],
                "departments": sample_chunk["departments"],
                "doc_types": sample_chunk["doc_types"],
                "score": round(file_score, 4),
                "excerpts": excerpts
            })

        scored_files.sort(key=lambda f: f["score"], reverse=True)

        # Paginate
        total_files = len(scored_files)
        total_pages = (total_files + per_page - 1) // per_page if total_files > 0 else 0
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_results = scored_files[start_idx:end_idx]

        return {
            "results": page_results,
            "total_files": total_files,
            "total_pages": total_pages,
            "page": page,
            "per_page": per_page,
            "query": query,
            "synonyms_used": synonyms_used,
            "exact_mode": exact_mode
        }

    def _highlight_text(self, text: str, terms: List[str]) -> str:
        escaped_text = html.escape(text)
        sorted_terms = sorted([t for t in terms if t.strip()], key=len, reverse=True)
        if not sorted_terms:
            return escaped_text

        pattern = re.compile(r'(' + '|'.join(re.escape(t) for t in sorted_terms) + r')', re.IGNORECASE)
        return pattern.sub(r'<mark>\1</mark>', escaped_text)
