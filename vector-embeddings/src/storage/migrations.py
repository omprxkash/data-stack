"""
Utilities for migrating data between storage backends.
Useful when you've outgrown ChromaDB and want to move to pgvector in production.
"""
from .base_store import VectorStore


def migrate(source: VectorStore, dest: VectorStore, collection: str | None = None, batch_size: int = 256) -> int:
    """Copy all vectors from `source` to `dest`. Returns total records migrated."""
    import numpy as np

    data = source.get_all_embeddings(collection)
    ids = data["ids"]
    embeddings = np.array(data["embeddings"], dtype=float)
    documents = data["documents"]
    metadatas = data["metadatas"]

    total = 0
    for start in range(0, len(ids), batch_size):
        end = start + batch_size
        dest.upsert(
            ids[start:end],
            embeddings[start:end],
            documents[start:end],
            metadatas[start:end],
        )
        total += len(ids[start:end])

    return total
