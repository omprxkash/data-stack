from .generator import EmbeddingGenerator
from .batch_processor import BatchProcessor
from .cache import EmbeddingCache

__all__ = ["EmbeddingGenerator", "BatchProcessor", "EmbeddingCache"]
from .utils import cosine_similarity, top_k_by_score, deduplicate
from .similarity import pairwise_cosine, nearest_in_batch
