from fastapi import APIRouter, Query
from pydantic import BaseModel
from ...embeddings.generator import EmbeddingGenerator
from ...storage.chroma_store import ChromaVectorStore
from ...search.semantic_search import SemanticSearch
from ...search.hybrid_search import HybridSearch

router = APIRouter()


class IngestRequest(BaseModel):
    documents: list[dict]
    collection: str = "default"


class SearchRequest(BaseModel):
    query: str
    collection: str = "default"
    n_results: int = 5
    mode: str = "semantic"   # "semantic" | "hybrid"
    filters: dict | None = None


def _store(collection: str) -> ChromaVectorStore:
    return ChromaVectorStore(collection_name=collection)


@router.post("/ingest")
def ingest(req: IngestRequest):
    gen = EmbeddingGenerator()
    store = _store(req.collection)
    ids = [d["id"] for d in req.documents]
    texts = [d["text"] for d in req.documents]
    metas = [d.get("metadata", {}) for d in req.documents]
    embeddings = gen.embed_batch(texts)
    store.upsert(ids, embeddings, texts, metas)
    return {"ingested": len(ids), "collection": req.collection}


@router.post("/search")
def search(req: SearchRequest):
    gen = EmbeddingGenerator()
    store = _store(req.collection)
    if req.mode == "hybrid":
        searcher = HybridSearch(store, gen)
        results = searcher.search(req.query, collection=req.collection, n_results=req.n_results)
    else:
        searcher = SemanticSearch(store, gen)
        results = searcher.search(req.query, n_results=req.n_results, where=req.filters)
    return {"results": results, "mode": req.mode}


class DeleteRequest(BaseModel):
    ids: list[str]
    collection: str = "default"


@router.delete("/documents")
def delete_documents(req: DeleteRequest):
    store = _store(req.collection)
    store.delete(req.ids)
    return {"deleted": len(req.ids), "collection": req.collection}


@router.get("/collections/{name}/count")
def collection_count(name: str):
    store = _store(name)
    return {"collection": name, "count": store.count()}
