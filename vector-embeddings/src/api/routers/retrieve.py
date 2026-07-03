from fastapi import APIRouter
from pydantic import BaseModel
from ...embeddings.generator import EmbeddingGenerator
from ...storage.chroma_store import ChromaVectorStore
from ...retrieval.pipeline import RetrievalPipeline

router = APIRouter()


class RetrieveRequest(BaseModel):
    question: str
    collection: str = "default"
    n: int = 5


@router.post("/retrieve")
def retrieve(req: RetrieveRequest):
    gen = EmbeddingGenerator()
    store = ChromaVectorStore(collection_name=req.collection)
    pipeline = RetrievalPipeline(store, gen)
    result = pipeline.query(req.question, n=req.n)
    return result


@router.get("/collections")
def list_collections():
    store = ChromaVectorStore()
    return {"collections": store.list_collections()}


class BatchRetrieveRequest(BaseModel):
    questions: list[str]
    collection: str = "default"
    n: int = 5


@router.post("/retrieve-batch")
def retrieve_batch(req: BatchRetrieveRequest):
    gen = EmbeddingGenerator()
    store = ChromaVectorStore(collection_name=req.collection)
    pipeline = RetrievalPipeline(store, gen)
    return {"results": [pipeline.query(q, n=req.n) for q in req.questions]}
