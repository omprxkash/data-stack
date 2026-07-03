from abc import ABC, abstractmethod
import numpy as np


class VectorStore(ABC):
    """Abstract interface every storage backend must implement."""

    @abstractmethod
    def upsert(
        self,
        ids: list[str],
        embeddings: np.ndarray,
        documents: list[str],
        metadatas: list[dict],
    ) -> None: ...

    @abstractmethod
    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> dict: ...

    @abstractmethod
    def list_collections(self) -> list[str]: ...

    @abstractmethod
    def get_all_embeddings(self, collection: str) -> dict:
        """Return {ids, embeddings, documents, metadatas} for the full collection."""
        ...
