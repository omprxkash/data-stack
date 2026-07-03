import numpy as np
import pytest
from src.embeddings.generator import EmbeddingGenerator


@pytest.fixture(scope="module")
def gen():
    return EmbeddingGenerator("fast")


def test_embed_returns_correct_dim(gen):
    vec = gen.embed("vector embeddings are useful")
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (gen.dim,)
    assert gen.dim == 384


def test_embed_is_normalised(gen):
    vec = gen.embed("test sentence")
    assert abs(np.linalg.norm(vec) - 1.0) < 1e-5


def test_embed_batch_shape(gen):
    texts = ["first sentence", "second sentence", "third sentence"]
    vecs = gen.embed_batch(texts)
    assert vecs.shape == (3, gen.dim)


def test_similar_texts_have_high_cosine(gen):
    v1 = gen.embed("the dog ran across the field")
    v2 = gen.embed("a dog was running through the grass")
    v3 = gen.embed("transformer architecture for language models")
    assert float(v1 @ v2) > float(v1 @ v3)


def test_model_variants_load():
    gen_quality = EmbeddingGenerator("quality")
    assert gen_quality.dim == 768
    vec = gen_quality.embed("hello world")
    assert vec.shape == (768,)


def test_embed_query_returns_list(gen):
    result = gen.embed_query("testing embed_query")
    assert isinstance(result, list)
    assert len(result) == gen.dim
    assert all(isinstance(v, float) for v in result)
