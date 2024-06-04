"""Test the `uint` module."""

import pytest

from tigerbeetle_py import uint


@pytest.fixture(
    name="uint_cls",
    params=(uint.UInt16, uint.UInt32, uint.UInt64, uint.UInt128),
)
def _uint_cls(request: pytest.FixtureRequest) -> uint.UInt:
    return request.param


@pytest.fixture(name="value", params=(0, "max"))
def _value(request: pytest.FixtureRequest, uint_cls: uint.UInt) -> int:
    if request.param == "max":
        return (1 << uint_cls.n_bits) - 1
    return request.param


def test_init(uint_cls: uint.UInt, value: int) -> None:
    u = uint_cls(value)
    assert int.from_bytes(u.memory, "little") == value

    assert u.int == value
    assert u.str == str(value)
    assert u.hex == hex(value).replace("0x", "").zfill(uint_cls.n_bytes * 2)

    with pytest.raises(TypeError):
        uint_cls("a")

    with pytest.raises(ValueError):
        uint_cls(-1)

    with pytest.raises(ValueError):
        uint_cls(1 << uint_cls.n_bits)


def test_operators(uint_cls: uint.UInt) -> None:
    v = (1 << uint_cls.n_bits) // 2 - 1
    u = uint_cls(v)

    assert u == u
    assert u == v
    assert u == int.from_bytes(u.memory, "little")
    assert u == uint_cls(v)
    assert u == uint_cls.from_bytes(u.memory)
    assert u != v - 1
    assert u != uint_cls(v - 1)
    assert u < v + 1
    assert u < uint_cls(v + 1)
    assert u <= v
    assert u <= v + 1
    assert u <= uint_cls(v)
    assert u <= uint_cls(v + 1)
    assert u > v - 1
    assert u > uint_cls(v - 1)
    assert u >= v
    assert u >= v - 1
    assert u >= uint_cls(v)
    assert u >= uint_cls(v - 1)
    assert u + 1 == v + 1
    assert u + 1 == uint_cls(v + 1)
    assert u - 1 == v - 1
    assert u - 1 == uint_cls(v - 1)
    assert u * 2 == v * 2
    assert u * 2 == uint_cls(v * 2)
    assert u // 2 == v // 2
    assert u // 2 == uint_cls(v // 2)
    assert u % 2 == v % 2
    assert u % 2 == uint_cls(v % 2)
    assert u << 1 == v << 1
    assert u << 1 == uint_cls(v << 1)
    assert u >> 1 == v >> 1
    assert u >> 1 == uint_cls(v >> 1)
    assert u & 1 == v & 1
    assert u & 1 == uint_cls(v & 1)
    assert u | 1 == v | 1
    assert u | 1 == uint_cls(v | 1)
    assert u ^ 1 == v ^ 1
    assert u ^ 1 == uint_cls(v ^ 1)

    # illegal operations
    with pytest.raises(TypeError):
        u / 2

    with pytest.raises(TypeError):
        ~u


def test_from_bytes(uint_cls: uint.UInt) -> None:
    v = (1 << uint_cls.n_bits) - 1
    u = uint_cls.from_bytes(v.to_bytes(uint_cls.n_bytes, "little"))

    assert int.from_bytes(u.memory, "little") == v

    with pytest.raises(ValueError):
        uint_cls.from_bytes(b"\x00" * (uint_cls.n_bytes - 1))

    with pytest.raises(ValueError):
        uint_cls.from_bytes(b"\x00" * (uint_cls.n_bytes + 1))


def test_from_tuple(uint_cls: uint.UInt) -> None:
    v = (1 << uint_cls.n_bits) - 1
    u = uint_cls.from_tuple(
        v >> uint_cls.n_bits // 2,
        v & (1 << uint_cls.n_bits // 2) - 1,
    )

    assert int.from_bytes(u.memory, "little") == v

    with pytest.raises(ValueError):
        uint_cls.from_tuple(0, -1)

    with pytest.raises(ValueError):
        uint_cls.from_tuple(1 << uint_cls.n_bits, 0)
