# data-stack

Three complementary layers of data infrastructure — async API endpoints, relational database patterns, and vector embeddings — kept together because they're almost always needed at the same time.

---

## What's inside

### `async-endpoints/`
A FastAPI service demonstrating async endpoint patterns: background tasks, streaming responses, dependency injection, and concurrent DB access. Includes a full Docker setup and pytest suite.

### `postgresql-patterns/`
A library of production PostgreSQL patterns: efficient pagination, upserts, advisory locks, recursive CTEs, and connection pooling configurations. Organised as runnable examples with a Docker Compose test database.

### `vector-embeddings/`
End-to-end embedding pipeline — generate embeddings from text and images, store them in a vector index, and run similarity search. Includes a lightweight frontend for exploring the embedding space and Jupyter notebooks walking through the math.

---

## Stack
Python · FastAPI · PostgreSQL · pgvector · sentence-transformers · FAISS · Docker
