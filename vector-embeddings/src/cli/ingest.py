"""
CLI: ingest documents from a directory into a ChromaDB collection.

Usage:
    python -m src.cli.ingest --dir data/sample_docs --collection demo
    python -m src.cli.ingest --dir /path/to/pdfs --collection research --chunk-size 256
"""
import argparse
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False

from ..embeddings.generator import EmbeddingGenerator
from ..storage.chroma_store import ChromaVectorStore
from ..retrieval.chunker import DocumentChunker
from ..embeddings.batch_processor import BatchProcessor


def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def read_pdf(path: Path) -> str:
    if not HAS_PYMUPDF:
        print(f"  [skip] {path.name} — install PyMuPDF to handle PDFs", file=sys.stderr)
        return ""
    doc = fitz.open(str(path))
    return "\n".join(page.get_text() for page in doc)


def main():
    parser = argparse.ArgumentParser(description="Ingest documents into a vector collection.")
    parser.add_argument("--dir", required=True, help="Directory containing .txt or .pdf files")
    parser.add_argument("--collection", default="default", help="Collection name (default: default)")
    parser.add_argument("--model", default="fast", help="Embedding model variant")
    parser.add_argument("--chunk-size", type=int, default=512)
    parser.add_argument("--overlap", type=int, default=64)
    parser.add_argument("--persist-dir", default="chroma_data")
    args = parser.parse_args()

    doc_dir = Path(args.dir)
    if not doc_dir.exists():
        print(f"Directory not found: {doc_dir}", file=sys.stderr)
        sys.exit(1)

    files = list(doc_dir.glob("*.txt")) + list(doc_dir.glob("*.pdf"))
    if not files:
        print(f"No .txt or .pdf files found in {doc_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(files)} file(s) in {doc_dir}")

    raw_docs = []
    for f in files:
        text = read_txt(f) if f.suffix == ".txt" else read_pdf(f)
        if text.strip():
            raw_docs.append({"id": f.stem, "text": text})

    chunker = DocumentChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    chunks = chunker.chunk_documents(raw_docs)
    print(f"Produced {len(chunks)} chunk(s)")

    gen = EmbeddingGenerator(args.model)
    store = ChromaVectorStore(persist_dir=args.persist_dir, collection_name=args.collection)
    processor = BatchProcessor(gen)

    total = 0
    for ids, embeddings, texts, metas in processor.process(chunks):
        store.upsert(ids, embeddings, texts, metas)
        total += len(ids)
        print(f"  Stored {total}/{len(chunks)} chunks…")

    print(f"\nDone. {total} chunks in collection '{args.collection}'.")


if __name__ == "__main__":
    main()


def ingest_text(text: str, doc_id: str, collection: str = "default",
                persist_dir: str = "chroma_data", model: str = "fast",
                chunk_size: int = 512, overlap: int = 64) -> int:
    """Programmatic entry point for single-document ingest. Returns chunk count."""
    gen = EmbeddingGenerator(model)
    store = ChromaVectorStore(persist_dir=persist_dir, collection_name=collection)
    chunker = DocumentChunker(chunk_size=chunk_size, overlap=overlap)
    chunks = chunker.chunk(text, source=doc_id)
    processor = BatchProcessor(gen)
    total = 0
    for ids, embeddings, texts, metas in processor.process(chunks):
        store.upsert(ids, embeddings, texts, metas)
        total += len(ids)
    return total
