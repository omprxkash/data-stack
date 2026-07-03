from ..embeddings.generator import EmbeddingGenerator
from ..storage.base_store import VectorStore


class RetrievalPipeline:
    """
    Extractive retrieval: embed the question, pull top passages from the store,
    return them ranked. No generation — what you get back is verbatim text from
    your documents.
    """

    def __init__(self, store: VectorStore, embedder: EmbeddingGenerator):
        self.store = store
        self.embedder = embedder

    def query(self, question: str, n: int = 5) -> dict:
        q_vec = self.embedder.embed(question)
        res = self.store.query(q_vec.tolist(), n_results=n)
        passages = res["documents"][0]
        ids = res["ids"][0]
        metas = res["metadatas"][0]
        distances = res["distances"][0]

        ranked = []
        for i, passage in enumerate(passages):
            ranked.append({
                "id": ids[i],
                "text": passage,
                "metadata": metas[i],
                "score": round(1.0 - distances[i], 4),
            })

        return {
            "passages": ranked,
            "sources": [r["metadata"].get("source", r["id"]) for r in ranked],
            "best_snippet": passages[0] if passages else None,
        }
