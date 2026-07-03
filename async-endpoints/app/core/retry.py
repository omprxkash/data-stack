import functools
import random
import time
from typing import Callable, Type


def retry(
    max_attempts: int = 3,
    backoff_base: float = 0.5,
    backoff_max: float = 30.0,
    jitter: bool = True,
    on_exceptions: tuple[Type[Exception], ...] = (Exception,),
):
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except on_exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        break
                    delay = min(backoff_base * (2 ** (attempt - 1)), backoff_max)
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    time.sleep(delay)
            raise RuntimeError(f"All {max_attempts} attempts failed") from last_exc  # type: ignore[misc]

        return wrapper

    return decorator
