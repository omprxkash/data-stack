import numpy as np
from sklearn.cluster import KMeans
from ..storage.base_store import VectorStore


class KMeansCluster:
    """Groups embeddings into k clusters and annotates each point with its label."""

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state

    def cluster(self, store: VectorStore, collection: str | None = None) -> list[dict]:
        data = store.get_all_embeddings(collection)
        ids = data["ids"]
        embeddings = np.array(data["embeddings"], dtype=float)
        docs = data["documents"]
        metas = data["metadatas"]

        if len(embeddings) < self.n_clusters:
            n_clusters = len(embeddings)
        else:
            n_clusters = self.n_clusters

        km = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init="auto")
        labels = km.fit_predict(embeddings)

        return [
            {
                "id": ids[i],
                "cluster": int(labels[i]),
                "text": docs[i][:120] if docs else "",
                "metadata": metas[i] if metas else {},
            }
            for i in range(len(ids))
        ]
