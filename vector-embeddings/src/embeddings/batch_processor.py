from typing import Generator
import numpy as np
from .generator import EmbeddingGenerator


class BatchProcessor:
    """Ingests a list of documents in chunks, yielding progress as it goes."""

    def __init__(self, generator: EmbeddingGenerator, batch_size: int = 64):
        self.generator = generator
        self.batch_size = batch_size

    def process(
        self, docs: list[dict]
    ) -> Generator[tuple[list[str], np.ndarray, list[dict]], None, None]:
        """Yield (ids, embeddings, metadatas) for each batch."""
        for start in range(0, len(docs), self.batch_size):
            batch = docs[start : start + self.batch_size]
            ids = [d["id"] for d in batch]
            texts = [d["text"] for d in batch]
            metas = [d.get("metadata", {}) for d in batch]
            embeddings = self.generator.embed_batch(texts, batch_size=self.batch_size)
            yield ids, embeddings, texts, metas
