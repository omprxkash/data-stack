import hashlib
import numpy as np
import joblib
import os
from pathlib import Path


class EmbeddingCache:
    """Disk-backed cache so we don't re-embed the same text twice."""

    def __init__(self, cache_dir: str = ".joblib_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, model_name: str, text: str) -> str:
        digest = hashlib.sha256(f"{model_name}::{text}".encode()).hexdigest()
        return digest

    def get(self, model_name: str, text: str) -> np.ndarray | None:
        path = self.cache_dir / self._key(model_name, text)
        if path.exists():
            return joblib.load(path)
        return None

    def set(self, model_name: str, text: str, embedding: np.ndarray) -> None:
        path = self.cache_dir / self._key(model_name, text)
        joblib.dump(embedding, path)

    def cached_embed(self, generator, text: str) -> np.ndarray:
        hit = self.get(generator.model_name, text)
        if hit is not None:
            return hit
        embedding = generator.embed(text)
        self.set(generator.model_name, text, embedding)
        return embedding
