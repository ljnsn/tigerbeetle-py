"""Unique monotolically increasing ID."""

import os
import threading
import time

from tigerbeetle_py._types.uint import UInt128


ID_LAST_TIMESTAMP = 0
ID_LAST_RANDOM = bytearray(10)
ID_MUTEX = threading.Lock()


def ID() -> UInt128:
    """
    Generate a Universally Unique and Sortable Identifier based on https://github.com/ulid/spec.

    Uint128 returned are guaranteed to be monotonically increasing when interpreted as little-endian.
    `ID()` is safe to call from multiple threads with monotonicity being sequentially consistent.
    """
    timestamp = int(time.time() * 1000)

    # Lock the mutex for global id variables.
    # Then ensure lastTimestamp is monotonically increasing & lastRandom changes each millisecond
    global ID_MUTEX
    global ID_LAST_TIMESTAMP
    global ID_LAST_RANDOM
    ID_MUTEX.acquire()

    id_last_random = memoryview(ID_LAST_RANDOM)

    if timestamp <= ID_LAST_TIMESTAMP:
        timestamp = ID_LAST_TIMESTAMP
    else:
        ID_LAST_TIMESTAMP = timestamp
        try:
            id_last_random[:] = bytearray(os.urandom(10))
        except Exception:
            ID_MUTEX.release()
            raise RuntimeError("os.urandom failed to provide random bytes")

    # Read out a uint80 from lastRandom as a uint64 and uint16.
    random_lo = int.from_bytes(id_last_random[:8], "little")
    random_hi = int.from_bytes(id_last_random[8:], "little")

    # Increment the random bits as a uint80 together, checking for overflow.
    # Go defines unsigned arithmetic to wrap around on overflow by default so check for zero.
    random_lo += 1
    if random_lo == 2**64:
        random_hi += 1
        if random_hi == 2**16:
            ID_MUTEX.release()
            raise RuntimeError("random bits overflow on monotonic increment")

    # Write incremented uint80 back to lastRandom and stop mutating global id variables.
    id_last_random[:8] = random_lo.to_bytes(8, "little")
    id_last_random[8:] = random_hi.to_bytes(2, "little")
    ID_MUTEX.release()

    # Create Uint128 from new timestamp and random.
    ulid = bytearray(16)
    _ulid = memoryview(ulid)
    _ulid[:8] = random_lo.to_bytes(8, "little")
    _ulid[8:10] = random_hi.to_bytes(2, "little")
    _ulid[10:12] = (timestamp & 0xFFFF).to_bytes(2, "little")
    _ulid[12:] = (timestamp >> 16).to_bytes(4, "little")
    return UInt128.from_bytes(ulid)
