"""Test the client."""

import pytest
from tigerbeetle_py import Client, bindings, uint

uint128 = uint.UInt128
uint64 = uint.UInt64
uint32 = uint.UInt32
uint16 = uint.UInt16


def test_create_accounts(tb_client: Client):
    """Test creating accounts."""
    account_a = bindings.Account(uint128(0xA), ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(uint128(0xB), ledger=uint32(1), code=uint16(2))

    results = tb_client.create_accounts([account_a, account_b])

    assert all(result.result == 0 for result in results)
