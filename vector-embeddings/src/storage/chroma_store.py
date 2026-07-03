import chromadb
import numpy as np
from .base_store import VectorStore


class ChromaVectorStore(VectorStore):
    """ChromaDB-backed vector store — great for local dev, no infrastructure needed."""

    def __init__(self, persist_dir: str = "chroma_data", collection_name: str = "default"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = collection_name
        self.collection = self._get_or_create(collection_name)

    def _get_or_create(self, name: str):
        return self.client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )

    def use_collection(self, name: str) -> None:
        self.collection_name = name
        self.collection = self._get_or_create(name)

    def upsert(
        self,
        ids: list[str],
        embeddings: np.ndarray,
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> dict:
        kwargs = dict(query_embeddings=[query_embedding], n_results=n_results, include=["documents", "metadatas", "distances"])
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def list_collections(self) -> list[str]:
        return [c.name for c in self.client.list_collections()]

    def get_all_embeddings(self, collection: str | None = None) -> dict:
        col = self._get_or_create(collection or self.collection_name)
        return col.get(include=["embeddings", "documents", "metadatas"])

    def delete(self, ids: list[str]) -> None:
        self.collection.delete(ids=ids)

    def count(self) -> int:
        return self.collection.count()
