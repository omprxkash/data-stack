"""Retry decorator tests."""

import time

import pytest

from app.core.retry import retry


def test_succeeds_first_try():
    calls = []

    @retry(max_attempts=3)
    def fn():
        calls.append(1)
        return "done"

    assert fn() == "done"
    assert len(calls) == 1


def test_retries_on_failure():
    calls = []

    @retry(max_attempts=3, backoff_base=0.01, jitter=False)
    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("not yet")
        return "ok"

    assert fn() == "ok"
    assert len(calls) == 3


def test_raises_after_max_attempts():
    calls = []

    @retry(max_attempts=3, backoff_base=0.01, jitter=False)
    def fn():
        calls.append(1)
        raise RuntimeError("always fails")

    with pytest.raises(RuntimeError):
        fn()
    assert len(calls) == 3


def test_only_retries_specified_exceptions():
    @retry(max_attempts=3, backoff_base=0.01, on_exceptions=(ValueError,))
    def fn():
        raise TypeError("wrong type")

    with pytest.raises(TypeError):
        fn()


def test_backoff_increases_with_attempts():
    delays = []
    original_sleep = time.sleep

    def mock_sleep(s):
        delays.append(s)

    import app.core.retry as r_module
    r_module.time.sleep = mock_sleep

    try:
        @retry(max_attempts=4, backoff_base=1.0, jitter=False)
        def fn():
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            fn()
    finally:
        r_module.time.sleep = original_sleep

    # backoff: 1, 2, 4 (3 sleeps for 4 attempts)
    assert len(delays) == 3
    assert delays[0] < delays[1] < delays[2]
