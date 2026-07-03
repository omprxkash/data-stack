from sentence_transformers import CrossEncoder


class CrossEncoderReranker:
    """Optional reranking step using a cross-encoder model."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, results: list[dict], top_k: int | None = None) -> list[dict]:
        if not results:
            return results
        pairs = [(query, r["text"]) for r in results]
        scores = self.model.predict(pairs)
        for i, r in enumerate(results):
            r["rerank_score"] = float(scores[i])
        reranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k] if top_k else reranked
