import numpy as np


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Return the cosine similarity between two already-normalised vectors."""
    return float(np.dot(a, b))


def top_k_by_score(results: list[dict], k: int) -> list[dict]:
    return sorted(results, key=lambda r: r["score"], reverse=True)[:k]


def deduplicate(results: list[dict], key: str = "id") -> list[dict]:
    seen, out = set(), []
    for r in results:
        if r[key] not in seen:
            seen.add(r[key])
            out.append(r)
    return out
