import tempfile
import pytest
from src.embeddings.generator import EmbeddingGenerator
from src.storage.chroma_store import ChromaVectorStore
from src.retrieval.chunker import DocumentChunker
from src.retrieval.pipeline import RetrievalPipeline


LONG_DOC = """
Vector embeddings represent text as dense numerical vectors in a high-dimensional space.
Items that are semantically similar end up geometrically close to each other.
This property makes embeddings extremely powerful for search and retrieval tasks.
A vector database stores these embeddings and provides fast approximate nearest-neighbour search.
ChromaDB is a popular local vector database that's easy to set up and use.
pgvector is a PostgreSQL extension that adds vector similarity search to Postgres.
Hybrid search combines BM25 keyword matching with dense semantic retrieval for better results.
"""


@pytest.fixture(scope="module")
def pipeline_fixture():
    gen = EmbeddingGenerator("fast")
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ChromaVectorStore(persist_dir=tmpdir, collection_name="ret_test")
        chunker = DocumentChunker(chunk_size=64, overlap=10)
        chunks = chunker.chunk(LONG_DOC.strip(), source="test_doc")
        ids = [c["id"] for c in chunks]
        texts = [c["text"] for c in chunks]
        metas = [c["metadata"] for c in chunks]
        embeddings = gen.embed_batch(texts)
        store.upsert(ids, embeddings, texts, metas)
        pipeline = RetrievalPipeline(store, gen)
        yield pipeline


def test_chunker_produces_chunks():
    chunker = DocumentChunker(chunk_size=50, overlap=10)
    chunks = chunker.chunk(LONG_DOC.strip(), source="doc")
    assert len(chunks) >= 2
    for c in chunks:
        assert "id" in c
        assert "text" in c
        assert c["metadata"]["source"] == "doc"


def test_pipeline_returns_passages(pipeline_fixture):
    result = pipeline_fixture.query("what is a vector database?", n=3)
    assert "passages" in result
    assert "sources" in result
    assert "best_snippet" in result
    assert len(result["passages"]) > 0
    assert result["best_snippet"] is not None


def test_pipeline_no_generation(pipeline_fixture):
    result = pipeline_fixture.query("how does hybrid search work?", n=3)
    for p in result["passages"]:
        assert "text" in p
        assert "score" in p
        # passages must come verbatim from the corpus — no generated content
        assert p["text"].strip() != ""


def test_pipeline_scores_ordered(pipeline_fixture):
    result = pipeline_fixture.query("ChromaDB vector similarity", n=4)
    scores = [p["score"] for p in result["passages"]]
    assert scores == sorted(scores, reverse=True)


def test_chunker_stats():
    chunker = DocumentChunker(chunk_size=50, overlap=10)
    chunks = chunker.chunk(LONG_DOC.strip(), source="stat_doc")
    stats = chunker.stats(chunks)
    assert stats["count"] == len(chunks)
    assert stats["min_words"] > 0
    assert stats["max_words"] >= stats["min_words"]
    assert stats["avg_words"] > 0


def test_markdown_chunker_via_pipeline():
    from src.retrieval.chunker_markdown import MarkdownChunker
    md = "# Embeddings\n\nEmbeddings encode semantic meaning into dense vectors.\n\n## Storage\n\nChromaDB stores these vectors persistently on disk."
    chunker = MarkdownChunker(chunk_size=50, overlap=5)
    chunks = chunker.chunk(md, source="md_doc")
    assert all("heading" in c["metadata"] for c in chunks)
    assert len(chunks) >= 2
