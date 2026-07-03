import numpy as np


def pairwise_cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarities between every row in `a` and every row in `b`.
    Both arrays should be L2-normalised; result is an (m, n) matrix.
    """
    return a @ b.T


def nearest_in_batch(query: np.ndarray, corpus: np.ndarray, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """Return indices and scores of the top-k rows in `corpus` closest to `query`."""
    scores = corpus @ query
    top_k = np.argsort(scores)[::-1][:k]
    return top_k, scores[top_k]
