import threading
import time
from enum import Enum


class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        cooldown: float = 30.0,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.cooldown = cooldown
        self.name = name

        self._state = State.CLOSED
        self._failures = 0
        self._opened_at: float | None = None
        self._lock = threading.Lock()

    @property
    def state(self) -> State:
        with self._lock:
            return self._current_state()

    def _current_state(self) -> State:
        if self._state == State.OPEN:
            if self._opened_at and (time.monotonic() - self._opened_at) >= self.cooldown:
                self._state = State.HALF_OPEN
        return self._state

    def call(self, fn, *args, **kwargs):
        with self._lock:
            state = self._current_state()
            if state == State.OPEN:
                raise CircuitBreakerOpen(f"Circuit '{self.name}' is OPEN")

        try:
            result = fn(*args, **kwargs)
        except Exception:
            with self._lock:
                self._record_failure()
            raise
        else:
            with self._lock:
                self._record_success()
            return result

    def _record_failure(self) -> None:
        self._failures += 1
        if self._state == State.HALF_OPEN or self._failures >= self.failure_threshold:
            self._state = State.OPEN
            self._opened_at = time.monotonic()

    def _record_success(self) -> None:
        self._failures = 0
        self._state = State.CLOSED
        self._opened_at = None

    def __repr__(self) -> str:
        return f"CircuitBreaker(name={self.name!r}, state={self._state.value}, failures={self._failures})"
