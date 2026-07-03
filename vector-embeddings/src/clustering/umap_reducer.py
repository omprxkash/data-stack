import numpy as np
import umap
from ..storage.base_store import VectorStore


class UMAPReducer:
    """Projects high-dimensional embeddings down to 2D for visualisation."""

    def __init__(self, n_neighbors: int = 15, min_dist: float = 0.1, random_state: int = 42):
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist
        self.random_state = random_state

    def reduce(self, store: VectorStore, collection: str | None = None) -> list[dict]:
        data = store.get_all_embeddings(collection)
        ids = data["ids"]
        embeddings = np.array(data["embeddings"], dtype=float)
        docs = data["documents"]
        metas = data["metadatas"]

        if len(embeddings) < 2:
            return []

        n_neighbors = min(self.n_neighbors, len(embeddings) - 1)
        reducer = umap.UMAP(
            n_components=2,
            n_neighbors=n_neighbors,
            min_dist=self.min_dist,
            metric="cosine",
            random_state=self.random_state,
        )
        coords = reducer.fit_transform(embeddings)

        return [
            {
                "id": ids[i],
                "x": float(coords[i, 0]),
                "y": float(coords[i, 1]),
                "text": docs[i][:120] if docs else "",
                "metadata": metas[i] if metas else {},
            }
            for i in range(len(ids))
        ]


    def to_dataframe(self, points: list[dict]):
        """Convert UMAP output to a pandas DataFrame for easy plotting."""
        try:
            import pandas as pd
            return pd.DataFrame(points)
        except ImportError:
            raise ImportError("Install pandas to use to_dataframe()")
