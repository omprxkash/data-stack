"""
CLI: run extractive retrieval and print ranked passages.

Usage:
    python -m src.cli.retrieve_cli --question "what is cosine similarity?" --collection demo
"""
import argparse
from ..embeddings.generator import EmbeddingGenerator
from ..storage.chroma_store import ChromaVectorStore
from ..retrieval.pipeline import RetrievalPipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--collection", default="default")
    parser.add_argument("--n", type=int, default=3)
    parser.add_argument("--persist-dir", default="chroma_data")
    args = parser.parse_args()

    gen = EmbeddingGenerator()
    store = ChromaVectorStore(persist_dir=args.persist_dir, collection_name=args.collection)
    result = RetrievalPipeline(store, gen).query(args.question, n=args.n)

    print(f'\nQuestion: "{args.question}"\n')
    print(f"Sources: {', '.join(result['sources'])}\n")
    print("Passages (ranked):")
    for i, p in enumerate(result["passages"], 1):
        print(f"\n  {i}. [{p['score']:.3f}] {p['metadata'].get('source', p['id'])}")
        print(f"     {p['text']}")


if __name__ == "__main__":
    main()
