import numpy as np
from ..embeddings.generator import EmbeddingGenerator
from ..storage.base_store import VectorStore


class SemanticSearch:
    def __init__(self, store: VectorStore, generator: EmbeddingGenerator):
        self.store = store
        self.generator = generator

    def search(self, query: str, n_results: int = 5, where: dict | None = None) -> list[dict]:
        q_vec = self.generator.embed(query).tolist()
        raw = self.store.query(q_vec, n_results=n_results, where=where)
        results = []
        ids = raw["ids"][0]
        docs = raw["documents"][0]
        metas = raw["metadatas"][0]
        distances = raw["distances"][0]
        for i, doc_id in enumerate(ids):
            results.append({
                "id": doc_id,
                "text": docs[i],
                "metadata": metas[i],
                "score": round(1.0 - distances[i], 4),
            })
        return results

    def search_batch(self, queries: list[str], n_results: int = 5) -> list[list[dict]]:
        """Run multiple queries in one call, embedding them as a batch."""
        q_vecs = self.generator.embed_batch(queries)
        return [
            self.search(q, n_results=n_results) for q in queries
        ]
