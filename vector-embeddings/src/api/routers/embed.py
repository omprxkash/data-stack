from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from ...embeddings.generator import EmbeddingGenerator

router = APIRouter()
_gen_cache: dict[str, EmbeddingGenerator] = {}


def get_generator(model: str = "fast") -> EmbeddingGenerator:
    if model not in _gen_cache:
        _gen_cache[model] = EmbeddingGenerator(model)
    return _gen_cache[model]


class EmbedRequest(BaseModel):
    text: str
    model: str = "fast"

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text must not be empty")
        return v


class EmbedBatchRequest(BaseModel):
    texts: list[str]
    model: str = "fast"

    @field_validator("texts")
    @classmethod
    def texts_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("texts must not be empty")
        return v


@router.post("/embed")
def embed_single(req: EmbedRequest):
    gen = get_generator(req.model)
    vec = gen.embed(req.text)
    return {"embedding": vec.tolist(), "dim": len(vec), "model": gen.model_name}


@router.post("/embed-batch")
def embed_batch(req: EmbedBatchRequest):
    gen = get_generator(req.model)
    vecs = gen.embed_batch(req.texts)
    return {"embeddings": vecs.tolist(), "count": len(vecs), "dim": vecs.shape[1], "model": gen.model_name}
