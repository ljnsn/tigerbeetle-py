"""Tests for ID()."""

import threading
import time

import pytest

from tigerbeetle_py import uid


def verifier() -> None:
    id_a = uid.ID()
    for i in range(1_000_000):
        if i % 1_000 == 0:
            time.sleep(1 * 1e-3)
        id_b = uid.ID()
        assert id_b > id_a
        id_a = id_b


def test_id_locally() -> None:
    """Verify monotonic IDs locally."""
    verifier()


@pytest.mark.slow
def test_id_threads() -> None:
    """Verify monotonic IDs across multiple threads."""
    concurrency = 10
    barrier = threading.Barrier(concurrency)

    def target():
        i = threading.get_ident()
        print(f"Thread {i} started")
        barrier.wait()
        print(f"Thread {i} running verifier")
        verifier()
        print(f"Thread {i} finished")

    threads = [threading.Thread(target=target) for _ in range(concurrency)]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
