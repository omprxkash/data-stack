"""Circuit breaker state machine tests."""

import time

import pytest

from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerOpen, State


def _failing():
    raise RuntimeError("downstream error")


def _ok():
    return "ok"


def test_starts_closed():
    cb = CircuitBreaker(failure_threshold=3)
    assert cb.state == State.CLOSED


def test_opens_after_threshold_failures():
    cb = CircuitBreaker(failure_threshold=3)
    for _ in range(3):
        with pytest.raises(RuntimeError):
            cb.call(_failing)
    assert cb.state == State.OPEN


def test_rejects_fast_when_open():
    cb = CircuitBreaker(failure_threshold=1)
    with pytest.raises(RuntimeError):
        cb.call(_failing)
    assert cb.state == State.OPEN
    with pytest.raises(CircuitBreakerOpen):
        cb.call(_ok)


def test_transitions_to_half_open_after_cooldown():
    cb = CircuitBreaker(failure_threshold=1, cooldown=0.05)
    with pytest.raises(RuntimeError):
        cb.call(_failing)
    assert cb.state == State.OPEN
    time.sleep(0.1)
    assert cb.state == State.HALF_OPEN


def test_closes_on_success_from_half_open():
    cb = CircuitBreaker(failure_threshold=1, cooldown=0.05)
    with pytest.raises(RuntimeError):
        cb.call(_failing)
    time.sleep(0.1)
    assert cb.state == State.HALF_OPEN
    result = cb.call(_ok)
    assert result == "ok"
    assert cb.state == State.CLOSED


def test_reopens_on_failure_from_half_open():
    cb = CircuitBreaker(failure_threshold=1, cooldown=0.05)
    with pytest.raises(RuntimeError):
        cb.call(_failing)
    time.sleep(0.1)
    assert cb.state == State.HALF_OPEN
    with pytest.raises(RuntimeError):
        cb.call(_failing)
    assert cb.state == State.OPEN


def test_state_enum_values():
    assert State.CLOSED.value == "closed"
    assert State.OPEN.value == "open"
    assert State.HALF_OPEN.value == "half_open"
