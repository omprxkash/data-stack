from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingGenerator:
    """Wraps sentence-transformers with a few preset model variants."""

    MODELS = {
        "fast": "all-MiniLM-L6-v2",          # 384d, quick
        "quality": "all-mpnet-base-v2",        # 768d, better recall
        "multilingual": "paraphrase-multilingual-MiniLM-L12-v2",
    }

    def __init__(self, model_name: str = "fast"):
        resolved = self.MODELS.get(model_name, model_name)
        self.model = SentenceTransformer(resolved)
        self.model_name = resolved
        self.dim: int = self.model.get_sentence_embedding_dimension()

    def embed(self, text: str) -> np.ndarray:
        return self.model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )


    def embed_query(self, text: str) -> list[float]:
        """Convenience wrapper returning a plain list (useful for API callers)."""
        return self.embed(text).tolist()
