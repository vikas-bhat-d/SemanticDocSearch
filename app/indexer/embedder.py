from threading import RLock, Semaphore
from typing import ClassVar, Dict, List, Optional, Tuple
from sentence_transformers import SentenceTransformer


class Embedder:
    _instances: ClassVar[Dict[Tuple[str, int], "Embedder"]] = {}
    _cache_lock: ClassVar[RLock] = RLock()

    def __new__(
        cls,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dimensions: int = 384,
        embedding_concurrency: int = 1,
        max_batch_size: Optional[int] = None,
    ):
        cache_key = (model_name, dimensions)
        with cls._cache_lock:
            instance = cls._instances.get(cache_key)
            if instance is None:
                instance = super().__new__(cls)
                instance._cache_key = cache_key
                cls._instances[cache_key] = instance
            return instance

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        dimensions: int = 384,
        embedding_concurrency: int = 1,
        max_batch_size: Optional[int] = None,
    ):
        if getattr(self, "_initialized", False):
            return

        self.model_name = model_name
        self.dimensions = dimensions
        self.max_batch_size = max_batch_size
        self._embedding_semaphore = Semaphore(max(1, embedding_concurrency))
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
        if self.max_batch_size and len(texts) > self.max_batch_size:
            raise ValueError(
                f"Embedding batch contains {len(texts)} texts; maximum is {self.max_batch_size}"
            )
        with self._embedding_semaphore:
            vectors = self.model.encode(
                texts,
                batch_size=min(32, len(texts)),
                show_progress_bar=False,
                normalize_embeddings=True,
            )
        return vectors.tolist() if hasattr(vectors, "tolist") else list(vectors)
