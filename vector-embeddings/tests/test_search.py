import tempfile
import pytest
import numpy as np
from src.embeddings.generator import EmbeddingGenerator
from src.storage.chroma_store import ChromaVectorStore
from src.search.semantic_search import SemanticSearch
from src.search.hybrid_search import HybridSearch


DOCS = [
    {"id": "doc1", "text": "Vector databases store embeddings for fast similarity search.", "metadata": {"source": "test"}},
    {"id": "doc2", "text": "Natural language processing transforms text into meaning.", "metadata": {"source": "test"}},
    {"id": "doc3", "text": "The transformer architecture uses self-attention mechanisms.", "metadata": {"source": "test"}},
    {"id": "doc4", "text": "BM25 is a bag-of-words keyword retrieval algorithm.", "metadata": {"source": "test"}},
    {"id": "doc5", "text": "Cosine similarity measures the angle between two vectors.", "metadata": {"source": "test"}},
]


@pytest.fixture(scope="module")
def populated_store():
    gen = EmbeddingGenerator("fast")
    with tempfile.TemporaryDirectory() as tmpdir:
        store = ChromaVectorStore(persist_dir=tmpdir, collection_name="test_col")
        texts = [d["text"] for d in DOCS]
        ids = [d["id"] for d in DOCS]
        metas = [d["metadata"] for d in DOCS]
        embeddings = gen.embed_batch(texts)
        store.upsert(ids, embeddings, texts, metas)
        yield store, gen


def test_semantic_search_returns_results(populated_store):
    store, gen = populated_store
    searcher = SemanticSearch(store, gen)
    results = searcher.search("how do vector spaces work?", n_results=3)
    assert len(results) == 3
    for r in results:
        assert "id" in r
        assert "text" in r
        assert "score" in r
        assert 0 <= r["score"] <= 1.0


def test_semantic_search_relevance(populated_store):
    store, gen = populated_store
    searcher = SemanticSearch(store, gen)
    results = searcher.search("similarity between vectors", n_results=3)
    top_id = results[0]["id"]
    assert top_id in ("doc1", "doc5")


def test_hybrid_search_returns_results(populated_store):
    store, gen = populated_store
    searcher = HybridSearch(store, gen, alpha=0.5)
    results = searcher.search("BM25 keyword retrieval", n_results=3)
    assert len(results) == 3
    assert all("bm25_score" in r for r in results)
    assert all("semantic_score" in r for r in results)


def test_hybrid_keyword_boost(populated_store):
    store, gen = populated_store
    searcher = HybridSearch(store, gen, alpha=0.1)
    results = searcher.search("BM25 keyword algorithm", n_results=5)
    top_id = results[0]["id"]
    assert top_id == "doc4"


def test_chroma_count(populated_store):
    store, _ = populated_store
    assert store.count() == len(DOCS)


def test_alpha_validation(populated_store):
    store, gen = populated_store
    import pytest
    searcher = HybridSearch(store, gen, alpha=0.5)
    with pytest.raises(ValueError):
        searcher.tune_alpha(1.5)
    searcher.tune_alpha(0.8)
    assert searcher.alpha == 0.8


def test_semantic_search_batch(populated_store):
    store, gen = populated_store
    from src.search.semantic_search import SemanticSearch
    searcher = SemanticSearch(store, gen)
    batch_results = searcher.search_batch(
        ["vector similarity", "keyword retrieval"], n_results=2
    )
    assert len(batch_results) == 2
    assert all(len(r) == 2 for r in batch_results)
