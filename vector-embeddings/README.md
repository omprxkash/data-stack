# vector-embeddings

**Search your own documents by meaning, not just keywords.**

I built this because I kept hitting the same wall: keyword search misses things that are obviously relevant, and plugging in a full LLM just to retrieve a passage feels like overkill. What I actually wanted was a clean, hackable toolkit that lets me embed text, store it in a vector database, and find the most relevant chunks for any question — without any black boxes in the way. This is that toolkit.

It handles the whole pipeline: chunking documents, generating embeddings, storing them in ChromaDB (for local dev) or PostgreSQL with pgvector (for production), running semantic and hybrid search, and returning ranked passages with their sources. No generated text, no mystery. If a passage comes back, it came from your corpus verbatim.

---

## What it does

- **Semantic search** — find passages that *mean* what you're asking, even if they don't share exact words
- **Hybrid search** — combine BM25 keyword scoring with dense semantic similarity for the best of both worlds
- **Extractive retrieval** — get back ranked passages and their sources, nothing fabricated
- **UMAP cluster explorer** — visualise how your document chunks relate to each other in 2D
- **REST API** — FastAPI server with endpoints for embedding, ingesting, searching, clustering, and retrieval
- **Minimal React UI** — a search bar + results view and a cluster scatter plot, nothing more than what's useful
- **CLI ingest tool** — point it at a folder of `.txt` or `.pdf` files and it handles the rest
- **Two storage backends** — ChromaDB for zero-config local use, pgvector for production Postgres

---

## Tech stack

| Layer | Library |
|---|---|
| Embeddings | sentence-transformers (all-MiniLM-L6-v2 · all-mpnet-base-v2) |
| Vector DB (dev) | ChromaDB |
| Vector DB (prod) | PostgreSQL + pgvector |
| Keyword search | rank-bm25 |
| Reranking | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| Dimensionality reduction | UMAP + KMeans (scikit-learn) |
| API | FastAPI + Uvicorn |
| PDF ingest | PyMuPDF |
| Frontend | React + TypeScript + Vite + Plotly |

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Python 3.11+ recommended. The sentence-transformers models download on first use (~90 MB for the fast model).

### 2. Ingest the sample documents

```bash
python -m src.cli.ingest --dir data/sample_docs --collection demo
```

This chunks the three sample documents, embeds them, and stores everything in a local ChromaDB database under `chroma_data/`. No Postgres needed for this step.

### 3. Run a search from Python

```python
from src.embeddings.generator import EmbeddingGenerator
from src.storage.chroma_store import ChromaVectorStore
from src.search.semantic_search import SemanticSearch

gen = EmbeddingGenerator("fast")
store = ChromaVectorStore(collection_name="demo")
search = SemanticSearch(store, gen)

results = search.search("how does self-attention work?", n_results=3)
for r in results:
    print(r["score"], r["text"][:120])
```

### 4. Or use the API

```bash
uvicorn src.api.main:app --reload
```

Then open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API explorer.

```bash
# Ingest via API
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"id": "doc1", "text": "Your text here", "metadata": {}}], "collection": "demo"}'

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "how does attention work?", "collection": "demo", "n_results": 5, "mode": "semantic"}'

# Extractive retrieval
curl -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{"question": "what is cosine similarity?", "collection": "demo"}'
```

### 5. Launch the UI

```bash
cd frontend
npm install
npm run dev
```

Opens at [http://localhost:5173](http://localhost:5173). The search tab talks to the API at `localhost:8000`. The cluster explorer calls `/cluster/umap` and renders the 2D scatter plot with Plotly.

---

## Optional: pgvector (production)

If you're running Postgres with pgvector installed, swap in `PgVectorStore`:

```python
from src.storage.pgvector_store import PgVectorStore

store = PgVectorStore(
    dsn="postgresql://user:password@localhost:5432/mydb",
    dim=384,
    collection_name="demo"
)
```

The schema (including the IVFFlat index) is created automatically on first use. Everything else — ingest, search, retrieval — works identically to the ChromaDB backend.

```sql
-- Install the extension in Postgres first:
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## How it works

```mermaid
graph LR
    A[Raw documents] --> B[DocumentChunker]
    B --> C[EmbeddingGenerator]
    C --> D[(Vector store\nChroma / pgvector)]
    D --> E{Query}
    E -->|semantic| F[SemanticSearch]
    E -->|hybrid| G[HybridSearch\nBM25 + cosine]
    E -->|retrieve| H[RetrievalPipeline]
    F --> I[Ranked results]
    G --> I
    H --> I
    D --> J[UMAPReducer]
    J --> K[ClusterViz]
```

**Chunking** splits documents into ~512-token windows with 64-token overlap so that context doesn't get cut off at chunk boundaries.

**Embedding** uses sentence-transformers to produce L2-normalised vectors. With normalised vectors, cosine similarity is just a dot product — fast and exact.

**Storage** writes the vectors alongside the original text and metadata. ChromaDB uses HNSW for approximate nearest-neighbour search; pgvector uses IVFFlat.

**Semantic search** embeds the query, queries the store for the nearest vectors, and returns results with cosine similarity scores.

**Hybrid search** computes BM25 keyword scores over the full corpus and combines them with the semantic scores via a weighted sum. The `alpha` parameter controls the balance (0 = pure keyword, 1 = pure semantic; default 0.5).

**Retrieval pipeline** is just semantic search with a clean output format: ranked passages, a list of sources, and the top snippet. Nothing is generated.

**UMAP + KMeans** fetches all embeddings, reduces them to 2D, and assigns cluster labels. The React frontend renders the result as an interactive scatter plot.

---

## Project structure

```
vector-embeddings/
├── src/
│   ├── embeddings/
│   │   ├── generator.py        # EmbeddingGenerator — wrap sentence-transformers
│   │   ├── batch_processor.py  # batched ingest with progress
│   │   └── cache.py            # joblib disk cache for repeated texts
│   ├── storage/
│   │   ├── base_store.py       # abstract VectorStore interface
│   │   ├── chroma_store.py     # ChromaDB backend
│   │   └── pgvector_store.py   # PostgreSQL + pgvector backend
│   ├── search/
│   │   ├── semantic_search.py  # cosine similarity search
│   │   ├── hybrid_search.py    # BM25 + semantic weighted blend
│   │   └── reranker.py         # optional cross-encoder reranking
│   ├── retrieval/
│   │   ├── chunker.py          # sentence-aware document chunker
│   │   └── pipeline.py         # extractive retrieval (no generation)
│   ├── clustering/
│   │   ├── umap_reducer.py     # UMAP 2D projection
│   │   └── kmeans_cluster.py   # KMeans cluster labels
│   ├── api/
│   │   ├── main.py             # FastAPI app + CORS
│   │   └── routers/
│   │       ├── embed.py        # POST /embed, POST /embed-batch
│   │       ├── search.py       # POST /ingest, POST /search
│   │       ├── cluster.py      # GET /cluster/umap
│   │       └── retrieve.py     # POST /retrieve, GET /collections
│   └── cli/
│       └── ingest.py           # CLI ingest tool
├── data/
│   └── sample_docs/            # three .txt files to try out of the box
├── frontend/
│   └── src/
│       ├── SearchUI.tsx        # search bar + results
│       └── ClusterViz.tsx      # UMAP scatter plot
├── notebooks/
│   ├── 01_embedding_basics.ipynb
│   ├── 02_semantic_search.ipynb
│   └── 03_retrieval_pipeline.ipynb
├── tests/
│   ├── test_generator.py
│   ├── test_search.py
│   └── test_retrieval.py
├── requirements.txt
└── README.md
```

---

## API reference

| Method | Path | What it does |
|---|---|---|
| `POST` | `/embed` | Embed a single text, returns vector + dimension |
| `POST` | `/embed-batch` | Embed a list of texts |
| `POST` | `/ingest` | Chunk + embed + store a list of documents |
| `POST` | `/search` | Semantic or hybrid search over a collection |
| `POST` | `/retrieve` | Extractive retrieval — ranked passages + sources |
| `GET` | `/cluster/umap` | UMAP 2D points for a collection |
| `GET` | `/collections` | List all stored collections |
| `GET` | `/health` | Health check |

Full request/response schemas are in the interactive docs at `/docs`.

---

## Running tests

```bash
pytest tests/ -v
```

The test suite doesn't need a running server or Postgres — it spins up a temporary ChromaDB instance for each module. First run downloads the embedding model, subsequent runs are fast.

---

## Notebooks

The three notebooks in `notebooks/` walk through the main concepts in order:

1. **01_embedding_basics** — generate embeddings, plot cosine similarity heatmap, try the disk cache
2. **02_semantic_search** — ingest sample docs, run semantic vs. hybrid queries side by side
3. **03_retrieval_pipeline** — full retrieval with passage ranking, then a UMAP cluster plot

Run them from the project root (or set the working directory accordingly) so the `src/` imports resolve.

---

## Limitations

A few things worth knowing before you build on this:

- **Scale**: ChromaDB is comfortable up to a few million vectors on a single machine. For larger corpora, pgvector with tuned IVFFlat lists, or a dedicated vector database, will serve you better.
- **Embedding quality**: `all-MiniLM-L6-v2` is fast and generally good, but it was trained mostly on English. Multilingual documents should use the `multilingual` model variant, and domain-specific corpora (legal, medical, code) may benefit from a domain-adapted model.
- **Chunking is crude**: The chunker splits on sentences and word counts, not semantic boundaries. For structured documents with sections and headings, a smarter chunking strategy will improve retrieval quality noticeably.
- **Reranking is optional and slow**: The cross-encoder reranker improves precision on the top results but runs the model once per result, so it's not suitable for latency-sensitive paths without caching.
- **No auth**: The FastAPI server has no authentication. Don't expose it to the public internet without adding at least an API key.

---

## Contributing

Contributions are welcome. If you find a bug or have an idea, open an issue first so we can discuss it before you put work into a PR.

**Author:** Om Prakash — [github.com/omprxkash](https://github.com/omprxkash)

---

MIT License © 2025 Om Prakash

---

## Evaluating retrieval quality

If you have a small labelled set of (question, relevant_passage_ids) pairs, you can measure how well the pipeline is doing before and after tuning chunk size, alpha, or the model:

```python
from src.retrieval.pipeline import RetrievalPipeline
from src.retrieval.evaluator import evaluate_pipeline

queries = [
    {"question": "how does self-attention work?", "relevant_ids": ["transformers::chunk::2"]},
    {"question": "what is a vector index?", "relevant_ids": ["vector_databases::chunk::1"]},
]

metrics = evaluate_pipeline(pipeline, queries, n=5)
print(metrics)
# {'precision@5': 0.4, 'recall@5': 1.0, 'mrr': 1.0}
```

---

## CLI tools

Beyond the ingest CLI, there are two other quick tools:

```bash
# Search from the terminal
python -m src.cli.search_cli --query "what is positional encoding?" --collection demo
python -m src.cli.search_cli --query "BM25 scoring" --collection demo --mode hybrid

# Extractive retrieval from the terminal
python -m src.cli.retrieve_cli --question "how does HNSW work?" --collection demo --n 3
```

---

## Migrating from ChromaDB to pgvector

When you're ready to move from a local ChromaDB setup to a production Postgres database:

```python
from src.storage.chroma_store import ChromaVectorStore
from src.storage.pgvector_store import PgVectorStore
from src.storage.migrations import migrate

src = ChromaVectorStore(persist_dir="chroma_data", collection_name="demo")
dst = PgVectorStore(dsn="postgresql://user:pass@localhost/mydb", dim=384, collection_name="demo")

migrated = migrate(src, dst)
print(f"Migrated {migrated} records")
```

The migration copies vectors, documents, and metadata in batches. It's safe to run while the ChromaDB instance is still serving reads — writes during migration may miss, so do a final drain if you need consistency.
