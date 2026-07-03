from src.retrieval.evaluator import precision_at_k, recall_at_k, mean_reciprocal_rank


def test_precision_at_k_perfect():
    assert precision_at_k(["a", "b", "c"], {"a", "b", "c"}, k=3) == 1.0


def test_precision_at_k_zero():
    assert precision_at_k(["x", "y", "z"], {"a", "b"}, k=3) == 0.0


def test_recall_at_k_partial():
    r = recall_at_k(["a", "x", "b"], {"a", "b", "c"}, k=3)
    assert abs(r - 2 / 3) < 1e-9


def test_mrr_first_hit():
    assert mean_reciprocal_rank(["a", "b", "c"], {"a"}) == 1.0


def test_mrr_second_hit():
    assert mean_reciprocal_rank(["x", "a", "b"], {"a"}) == 0.5


def test_mrr_no_hit():
    assert mean_reciprocal_rank(["x", "y"], {"a"}) == 0.0
