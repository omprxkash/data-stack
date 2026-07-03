from src.retrieval.chunker_markdown import MarkdownChunker


MD = """
# Introduction

Vector embeddings represent text as dense numerical vectors.
Semantically similar texts have vectors that are close in the space.

## How it works

The model processes the text and outputs a fixed-size vector.
This vector can then be compared to others using cosine similarity.

### Indexing

Storing these vectors in an HNSW index enables fast retrieval.
"""


def test_markdown_chunker_preserves_headings():
    chunker = MarkdownChunker(chunk_size=100, overlap=10)
    chunks = chunker.chunk(MD.strip(), source="test_md")
    headings = [c["metadata"]["heading"] for c in chunks]
    assert any(h == "Introduction" for h in headings)
    assert any(h in ("How it works", "Indexing") for h in headings)


def test_markdown_chunker_produces_chunks():
    chunker = MarkdownChunker()
    chunks = chunker.chunk(MD.strip(), source="test_md")
    assert len(chunks) > 0
    for c in chunks:
        assert "text" in c
        assert "heading" in c["metadata"]
