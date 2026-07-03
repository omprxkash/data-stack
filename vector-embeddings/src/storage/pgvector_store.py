import json
import numpy as np
import psycopg2
import psycopg2.extras
from .base_store import VectorStore

SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    collection  TEXT NOT NULL DEFAULT 'default',
    content     TEXT NOT NULL,
    embedding   vector({dim}),
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
"""


class PgVectorStore(VectorStore):
    """PostgreSQL + pgvector backend for production-scale workloads."""

    def __init__(self, dsn: str, dim: int = 384, collection_name: str = "default"):
        self.dsn = dsn
        self.dim = dim
        self.collection_name = collection_name
        self.conn = psycopg2.connect(dsn)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL.format(dim=self.dim))
        self.conn.commit()

    def use_collection(self, name: str) -> None:
        self.collection_name = name

    def upsert(
        self,
        ids: list[str],
        embeddings: np.ndarray,
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        rows = [
            (ids[i], self.collection_name, documents[i], embeddings[i].tolist(), json.dumps(metadatas[i]))
            for i in range(len(ids))
        ]
        with self.conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO documents (id, collection, content, embedding, metadata)
                VALUES %s
                ON CONFLICT (id) DO UPDATE
                  SET content = EXCLUDED.content,
                      embedding = EXCLUDED.embedding,
                      metadata = EXCLUDED.metadata
                """,
                rows,
            )
        self.conn.commit()

    def query(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None,
    ) -> dict:
        vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
        sql = """
            SELECT id, content, metadata,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            WHERE collection = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (vec_str, self.collection_name, vec_str, n_results))
            rows = cur.fetchall()

        ids, docs, metas, distances = [], [], [], []
        for row in rows:
            ids.append(row[0])
            docs.append(row[1])
            metas.append(row[2] or {})
            distances.append(1.0 - float(row[3]))  # convert similarity → distance

        return {"ids": [ids], "documents": [docs], "metadatas": [metas], "distances": [distances]}

    def list_collections(self) -> list[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT collection FROM documents ORDER BY collection")
            return [r[0] for r in cur.fetchall()]

    def get_all_embeddings(self, collection: str | None = None) -> dict:
        col = collection or self.collection_name
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT id, content, embedding, metadata FROM documents WHERE collection = %s",
                (col,),
            )
            rows = cur.fetchall()
        ids, docs, embeddings, metas = [], [], [], []
        for row in rows:
            ids.append(row[0])
            docs.append(row[1])
            embeddings.append(row[2])
            metas.append(row[3] or {})
        return {"ids": ids, "documents": docs, "embeddings": embeddings, "metadatas": metas}
