"""
CLI: run a quick search against a ChromaDB collection.

Usage:
    python -m src.cli.search_cli --query "how does attention work?" --collection demo
    python -m src.cli.search_cli --query "BM25 keyword" --collection demo --mode hybrid
"""
import argparse
from ..embeddings.generator import EmbeddingGenerator
from ..storage.chroma_store import ChromaVectorStore
from ..search.semantic_search import SemanticSearch
from ..search.hybrid_search import HybridSearch


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--collection", default="default")
    parser.add_argument("--mode", choices=["semantic", "hybrid"], default="semantic")
    parser.add_argument("--n", type=int, default=5)
    parser.add_argument("--model", default="fast")
    parser.add_argument("--persist-dir", default="chroma_data")
    args = parser.parse_args()

    gen = EmbeddingGenerator(args.model)
    store = ChromaVectorStore(persist_dir=args.persist_dir, collection_name=args.collection)

    if args.mode == "hybrid":
        results = HybridSearch(store, gen).search(args.query, collection=args.collection, n_results=args.n)
    else:
        results = SemanticSearch(store, gen).search(args.query, n_results=args.n)

    print(f'\nQuery: "{args.query}"  mode={args.mode}  collection={args.collection}\n')
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['score']:.3f}] {r['id']}")
        print(f"     {r['text'][:200]}\n")


if __name__ == "__main__":
    main()
