"""TB client helpers."""

import os
import threading
import time


def to_uint128(x: int) -> tuple[int, int]:
    b = f"{x:0>128b}"
    assert len(b) == 128, f"expected 128 bits, got {len(b)}"
    return int(b[:64], 2), int(b[64:], 2)


def from_uint128(high: int, low: int) -> int:
    mask = 1 << 64
    if high == 0 and low == 0:
        return 0
    if high < 0:
        high = high + mask
    if low < 0:
        low = low + mask
    return low + high * mask


ID_LAST_TIMESTAMP = 0
ID_LAST_RANDOM = bytearray(10)
ID_MUTEX = threading.Lock()


def ID() -> int:
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

    if timestamp <= ID_LAST_TIMESTAMP:
        timestamp = ID_LAST_TIMESTAMP
    else:
        ID_LAST_TIMESTAMP = timestamp
        try:
            ID_LAST_RANDOM = bytearray(os.urandom(10))
        except Exception:
            ID_MUTEX.release()
            raise RuntimeError("os.urandom failed to provide random bytes")

    _id_last_random = memoryview(ID_LAST_RANDOM)
    # Read out a uint80 from lastRandom as a uint64 and uint16.
    random_lo = int.from_bytes(_id_last_random[:8], "little")
    random_hi = int.from_bytes(_id_last_random[8:], "little")

    # Increment the random bits as a uint80 together, checking for overflow.
    # Go defines unsigned arithmetic to wrap around on overflow by default so check for zero.
    random_lo += 1
    if random_lo == 2**64:
        random_hi += 1
        if random_hi == 2**16:
            ID_MUTEX.release()
            raise RuntimeError("random bits overflow on monotonic increment")

    # Write incremented uint80 back to lastRandom and stop mutating global id variables.
    _id_last_random[:8] = random_lo.to_bytes(8, "little")
    _id_last_random[8:] = random_hi.to_bytes(2, "little")
    ID_MUTEX.release()

    # Create Uint128 from new timestamp and random.
    ulid = bytearray(16)
    _ulid = memoryview(ulid)
    timestamp_bin = f"{timestamp:048b}"
    _ulid[:8] = random_lo.to_bytes(8, "little")
    _ulid[8:10] = random_hi.to_bytes(2, "little")
    _ulid[10:12] = int(timestamp_bin[-16:], 2).to_bytes(2, "little")
    _ulid[12:] = (timestamp >> 16).to_bytes(4, "little")
    return int.from_bytes(ulid, "little")
