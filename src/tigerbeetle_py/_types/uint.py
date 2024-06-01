"""Unsigned integer."""

Buffer = bytes | bytearray | memoryview


def _int_to_bytes(n: int, length: int) -> bytes:
    return n.to_bytes(length, "little")


def _bytes_to_int(b: Buffer) -> int:
    return int.from_bytes(b, "little")


class UInt:
    """Unsigned integer."""

    __slots__ = ("memory", "max_bits")

    max_bits: int

    def __init__(self, integer: int) -> None:
        if not isinstance(integer, int):
            raise TypeError("integer must be an integer")
        if integer < 0:
            raise ValueError("integer must be non-negative")
        if integer.bit_length() > self.max_bits:
            msg = f"integer must be less than 2**{self.max_bits}"
            raise ValueError(msg)
        self.memory = memoryview(_int_to_bytes(integer, self.n_bytes))

    def __hash__(self) -> int:
        return hash(self.memory)

    def __bytes__(self) -> bytes:
        return self.bytes

    def __int__(self) -> int:
        return self.int

    def __float__(self) -> float:
        return self.float

    def __index__(self) -> int:
        return self.int

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({int(self)})"

    def __str__(self) -> str:
        return self.str

    def __add__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int + other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int + _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int + other)
        if isinstance(other, str):
            return self.__class__(self.int + int(other))
        return NotImplemented

    def __radd__(self, other: object) -> "UInt":
        return self.__add__(other)

    def __iadd__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            self.memory = _int_to_bytes(self.int + other.int, self.n_bytes)
        elif isinstance(other, (bytes, memoryview)):
            self.memory = _int_to_bytes(self.int + _bytes_to_int(other), self.n_bytes)
        elif isinstance(other, int):
            self.memory = _int_to_bytes(self.int + other, self.n_bytes)
        elif isinstance(other, str):
            self.memory = _int_to_bytes(self.int + int(other), self.n_bytes)
        else:
            return NotImplemented
        return self

    def __sub__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int - other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int - _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int - other)
        if isinstance(other, str):
            return self.__class__(self.int - int(other))
        return NotImplemented

    def __mul__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int * other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int * _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int * other)
        if isinstance(other, str):
            return self.__class__(self.int * int(other))
        return NotImplemented

    def __divmod__(self, other: object) -> tuple["UInt", "UInt"]:
        if isinstance(other, UInt):
            return self.__class__(self.int // other.int), self.__class__(
                self.int % other.int
            )
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int // _bytes_to_int(other)), self.__class__(
                self.int % _bytes_to_int(other)
            )
        if isinstance(other, int):
            return self.__class__(self.int // other), self.__class__(self.int % other)
        if isinstance(other, str):
            return self.__class__(self.int // int(other)), self.__class__(
                self.int % int(other)
            )
        return NotImplemented

    def __floordiv__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int // other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int // _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int // other)
        if isinstance(other, str):
            return self.__class__(self.int // int(other))
        return NotImplemented

    def __mod__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int % other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int % _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int % other)
        if isinstance(other, str):
            return self.__class__(self.int % int(other))
        return NotImplemented

    def __pow__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int**other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int ** _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int**other)
        if isinstance(other, str):
            return self.__class__(self.int ** int(other))
        return NotImplemented

    def __lshift__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int << other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int << _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int << other)
        if isinstance(other, str):
            return self.__class__(self.int << int(other))
        return NotImplemented

    def __rshift__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int >> other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int >> _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int >> other)
        if isinstance(other, str):
            return self.__class__(self.int >> int(other))
        return NotImplemented

    def __and__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int & other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int & _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int & other)
        if isinstance(other, str):
            return self.__class__(self.int & int(other))
        return NotImplemented

    def __or__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int | other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int | _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int | other)
        if isinstance(other, str):
            return self.__class__(self.int | int(other))
        return NotImplemented

    def __xor__(self, other: object) -> "UInt":
        if isinstance(other, UInt):
            return self.__class__(self.int ^ other.int)
        if isinstance(other, (bytes, memoryview)):
            return self.__class__(self.int ^ _bytes_to_int(other))
        if isinstance(other, int):
            return self.__class__(self.int ^ other)
        if isinstance(other, str):
            return self.__class__(self.int ^ int(other))
        return NotImplemented

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UInt):
            return self.memory == other.memory
        if isinstance(other, (bytes, memoryview)):
            return self.memory == other
        if isinstance(other, int):
            return self.int == other
        if isinstance(other, str):
            return self.str == other
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, UInt):
            return self.memory != other.memory
        if isinstance(other, (bytes, memoryview)):
            return self.memory != other
        if isinstance(other, int):
            return self.int != other
        if isinstance(other, str):
            return self.str != other
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, UInt):
            return self.int < other.int
        if isinstance(other, (bytes, memoryview)):
            return self.int < _bytes_to_int(other)
        if isinstance(other, int):
            return self.int < other
        if isinstance(other, str):
            return self.int < int(other)
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, UInt):
            return self.int > other.int
        if isinstance(other, (bytes, memoryview)):
            return self.int > _bytes_to_int(other)
        if isinstance(other, int):
            return self.int > other
        if isinstance(other, str):
            return self.int > int(other)
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, UInt):
            return self.int <= other.int
        if isinstance(other, (bytes, memoryview)):
            return self.int <= _bytes_to_int(other)
        if isinstance(other, int):
            return self.int <= other
        if isinstance(other, str):
            return self.int <= int(other)
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, UInt):
            return self.int >= other.int
        if isinstance(other, (bytes, memoryview)):
            return self.int >= _bytes_to_int(other)
        if isinstance(other, int):
            return self.int >= other
        if isinstance(other, str):
            return self.int >= int(other)
        return NotImplemented

    def __tuple__(self) -> tuple[int, int]:
        return self.tuple

    def __bool__(self) -> bool:
        return bool(self.int)

    @classmethod
    @property
    def n_bytes(cls) -> int:
        return cls.max_bits // 8

    @property
    def high(self) -> int:
        return _bytes_to_int(self.memory[self.n_bytes // 2 :])

    @property
    def low(self) -> int:
        return _bytes_to_int(self.memory[: self.n_bytes // 2])

    @property
    def int(self) -> int:
        return _bytes_to_int(self.memory)

    @property
    def bytes(self) -> bytes:
        return bytes(self.memory)

    @property
    def hex(self) -> str:
        return self.bytes.hex()

    @property
    def bin(self) -> str:
        return bin(self.int).lstrip("0b").zfill(self.max_bits)

    @property
    def str(self) -> str:
        return str(self.int)

    @property
    def tuple(self) -> tuple[int, int]:
        return self.high, self.low

    @classmethod
    def from_bytes(cls, b: Buffer) -> "UInt":
        if not isinstance(b, Buffer):
            raise TypeError("b must be bytes, bytearray or memoryview")
        if len(b) != cls.n_bytes:
            msg = f"b must be {cls.n_bytes} bytes, got {len(b)}"
            raise ValueError(msg)
        return cls(_bytes_to_int(b))

    @classmethod
    def from_tuple(cls, high: int, low: int) -> "UInt":
        if not isinstance(high, int):
            raise TypeError("high must be an integer")
        if not isinstance(low, int):
            raise TypeError("low must be an integer")
        if high < 0:
            raise ValueError("high must be non-negative")
        if low < 0:
            raise ValueError("low must be non-negative")
        if high.bit_length() > cls.max_bits // 2:
            msg = f"high must be less than 2**{cls.max_bits // 2}"
            raise ValueError(msg)
        if low.bit_length() > cls.max_bits // 2:
            msg = f"low must be less than 2**{cls.max_bits // 2}"
            raise ValueError(msg)
        return cls((high << cls.max_bits // 2) | low)


class UInt128(UInt):
    """128-bit unsigned integer."""

    max_bits = 128


class UInt64(UInt):
    """64-bit unsigned integer."""

    max_bits = 64


class UInt32(UInt):
    """32-bit unsigned integer."""

    max_bits = 32


class UInt16(UInt):
    """16-bit unsigned integer."""

    max_bits = 16
