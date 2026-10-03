from threading import RLock
from typing import ClassVar, Dict, List, Tuple
from sentence_transformers import SentenceTransformer


class Embedder:
    _instances: ClassVar[Dict[Tuple[str, int], "Embedder"]] = {}
    _cache_lock: ClassVar[RLock] = RLock()

    def __new__(cls, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", dimensions: int = 384):
        cache_key = (model_name, dimensions)
        with cls._cache_lock:
            instance = cls._instances.get(cache_key)
            if instance is None:
                instance = super().__new__(cls)
                instance._cache_key = cache_key
                cls._instances[cache_key] = instance
            return instance

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2", dimensions: int = 384):
        if getattr(self, "_initialized", False):
            return

        self.model_name = model_name
        self.dimensions = dimensions
        with self._cache_lock:
            if getattr(self, "_initialized", False):
                return
            try:
                self.model = SentenceTransformer(model_name)
                self._initialized = True
            except Exception:
                self._instances.pop(self._cache_key, None)
                raise

    @classmethod
    def clear_cache(cls):
        """Clear cached models, primarily for tests or explicit model resets."""
        with cls._cache_lock:
            cls._instances.clear()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        vectors = self.model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return vectors.tolist()
