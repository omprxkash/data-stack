-- pgvector schema for vector-embeddings
-- Run this once in your PostgreSQL database before using PgVectorStore

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    collection  TEXT NOT NULL DEFAULT 'default',
    content     TEXT NOT NULL,
    embedding   vector(384),
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- IVFFlat index — tune `lists` based on your corpus size
-- Rule of thumb: lists ≈ sqrt(num_rows)
CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS documents_collection_idx
    ON documents (collection);
