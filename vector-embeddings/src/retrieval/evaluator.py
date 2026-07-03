"""
Simple retrieval evaluation — precision@k and recall@k against a known relevant set.
Useful for offline benchmarking before and after tuning chunk size or alpha.
"""


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top_k = retrieved[:k]
    return len(set(top_k) & relevant) / k if k else 0.0


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    top_k = retrieved[:k]
    return len(set(top_k) & relevant) / len(relevant) if relevant else 0.0


def mean_reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for i, r in enumerate(retrieved, 1):
        if r in relevant:
            return 1.0 / i
    return 0.0


def evaluate_pipeline(pipeline, queries: list[dict], n: int = 5) -> dict:
    """
    queries: list of {question, relevant_ids} dicts
    Returns average precision@k, recall@k, MRR.
    """
    p_at_k, r_at_k, mrr = [], [], []
    for q in queries:
        result = pipeline.query(q["question"], n=n)
        retrieved = [p["id"] for p in result["passages"]]
        relevant = set(q["relevant_ids"])
        p_at_k.append(precision_at_k(retrieved, relevant, n))
        r_at_k.append(recall_at_k(retrieved, relevant, n))
        mrr.append(mean_reciprocal_rank(retrieved, relevant))
    return {
        f"precision@{n}": round(sum(p_at_k) / len(p_at_k), 4) if p_at_k else 0,
        f"recall@{n}": round(sum(r_at_k) / len(r_at_k), 4) if r_at_k else 0,
        "mrr": round(sum(mrr) / len(mrr), 4) if mrr else 0,
    }
