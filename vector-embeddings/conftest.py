import pytest


def pytest_configure(config):
    # Silence tqdm progress bars during tests
    import os
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
