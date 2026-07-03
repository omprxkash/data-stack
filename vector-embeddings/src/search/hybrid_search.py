import numpy as np
from rank_bm25 import BM25Okapi
from ..embeddings.generator import EmbeddingGenerator
from ..storage.base_store import VectorStore


class HybridSearch:
    """BM25 keyword score + cosine semantic score, blended by alpha."""

    def __init__(
        self,
        store: VectorStore,
        generator: EmbeddingGenerator,
        alpha: float = 0.5,
    ):
        self.store = store
        self.generator = generator
        self.alpha = alpha  # 0 = pure BM25, 1 = pure semantic

    def search(self, query: str, collection: str | None = None, n_results: int = 5) -> list[dict]:
        all_data = self.store.get_all_embeddings(collection)
        ids = all_data["ids"]
        docs = all_data["documents"]
        embeddings = np.array(all_data["embeddings"])
        metas = all_data["metadatas"]

        if not ids:
            return []

        # BM25 scores
        tokenised = [d.lower().split() for d in docs]
        bm25 = BM25Okapi(tokenised)
        bm25_scores = np.array(bm25.get_scores(query.lower().split()), dtype=float)
        if bm25_scores.max() > 0:
            bm25_scores /= bm25_scores.max()

        # Semantic scores
        q_vec = self.generator.embed(query)
        sem_scores = (embeddings @ q_vec).astype(float)
        if sem_scores.max() > 0:
            sem_scores /= sem_scores.max()

        combined = (1 - self.alpha) * bm25_scores + self.alpha * sem_scores
        top_indices = np.argsort(combined)[::-1][:n_results]

        return [
            {
                "id": ids[i],
                "text": docs[i],
                "metadata": metas[i],
                "score": round(float(combined[i]), 4),
                "bm25_score": round(float(bm25_scores[i]), 4),
                "semantic_score": round(float(sem_scores[i]), 4),
            }
            for i in top_indices
        ]


    def tune_alpha(self, alpha: float) -> None:
        """Adjust the semantic/keyword blend without recreating the searcher."""
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be between 0 and 1")
        self.alpha = alpha
