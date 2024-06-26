"""Test the client."""

import concurrent.futures

import pytest

from tigerbeetle_py import Client, bindings, uint, uid

uint128 = uint.UInt128
uint64 = uint.UInt64
uint32 = uint.UInt32
uint16 = uint.UInt16


@pytest.fixture(name="account_a_id")
def account_a_id_ifx() -> uint128:
    """Return the account A ID."""
    return uid.ID()


@pytest.fixture(name="account_b_id")
def account_b_id_ifx() -> uint128:
    """Return the account B ID."""
    return uid.ID()


@pytest.fixture(name="transfer_a_id")
def transfer_a_id_ifx() -> uint128:
    """Return the transfer A ID."""
    return uid.ID()


@pytest.fixture(name="transfer_b_id")
def transfer_b_id_ifx() -> uint128:
    """Return the transfer B ID."""
    return uid.ID()


def test_client(tb_client: Client) -> None:
    """Test the test method."""
    assert 1


def test_create_accounts(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
) -> None:
    """Test creating accounts."""
    account_a = bindings.Account(account_a_id, ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(account_b_id, ledger=uint32(1), code=uint16(2))

    results = tb_client.create_accounts([account_a, account_b])

    assert all(result.result == 0 for result in results)


def test_lookup_accounts(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
) -> None:
    """Test looking up accounts."""
    account_a = bindings.Account(uint128(0xC), ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(uint128(0xD), ledger=uint32(1), code=uint16(2))
    tb_client.create_accounts([account_a, account_b])

    accounts = tb_client.lookup_accounts([uint128(0xC), uint128(0xD)])

    assert len(accounts) == 2

    acc_a = accounts[0]
    assert acc_a.ledger == 1
    assert acc_a.code == 1
    assert acc_a.flags == 0
    assert acc_a.debits_pending == 0
    assert acc_a.debits_posted == 0
    assert acc_a.credits_pending == 0
    assert acc_a.credits_posted == 0
    assert acc_a.timestamp != 0
    # assert sys.getsizeof(acc_a) == 128

    acc_b = accounts[1]
    assert acc_b.ledger == 1
    assert acc_b.code == 2
    assert acc_b.flags == 0
    assert acc_b.debits_pending == 0
    assert acc_b.debits_posted == 0
    assert acc_b.credits_pending == 0
    assert acc_b.credits_posted == 0
    assert acc_b.timestamp != 0
    # assert sys.getsizeof(acc_b) == 128


def test_create_transfers(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
    transfer_a_id: uint128,
    transfer_b_id: uint128,
) -> None:
    """Test creating transfers."""
    account_a = bindings.Account(account_a_id, ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(account_b_id, ledger=uint32(1), code=uint16(2))
    tb_client.create_accounts([account_a, account_b])

    transfer_a = bindings.Transfer(
        transfer_a_id,
        debit_account_id=account_a_id,
        credit_account_id=account_b_id,
        amount=uint64(100),
        ledger=uint32(1),
        code=uint16(1),
    )
    transfer_b = bindings.Transfer(
        transfer_b_id,
        debit_account_id=account_b_id,
        credit_account_id=account_a_id,
        amount=uint64(50),
        ledger=uint32(1),
        code=uint16(1),
    )

    results = tb_client.create_transfers([transfer_a, transfer_b])

    assert all(result.result == 0 for result in results)

    accounts = tb_client.lookup_accounts([account_a_id, account_b_id])

    account_a = accounts[0]
    assert account_a.debits_pending == 0
    assert account_a.debits_posted == 100
    assert account_a.credits_pending == 0
    assert account_a.credits_posted == 50

    account_b = accounts[1]
    assert account_b.debits_pending == 0
    assert account_b.debits_posted == 50
    assert account_b.credits_pending == 0
    assert account_b.credits_posted == 100


def test_create_linked_transfers(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
    transfer_a_id: uint128,
) -> None:
    """Test creating linked transfers."""
    account_a = bindings.Account(account_a_id, ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(account_b_id, ledger=uint32(1), code=uint16(2))
    tb_client.create_accounts([account_a, account_b])

    transfer_a = bindings.Transfer(
        transfer_a_id,
        debit_account_id=account_a_id,
        credit_account_id=account_b_id,
        amount=uint64(100),
        ledger=uint32(1),
        code=uint16(1),
        flags=bindings.AccountFlags(linked=True).to_uint16(),
    )
    transfer_b = bindings.Transfer(
        transfer_a_id,
        debit_account_id=account_a_id,
        credit_account_id=account_b_id,
        amount=uint64(100),
        ledger=uint32(1),
        code=uint16(1),
    )

    results = tb_client.create_transfers([transfer_a, transfer_b])

    assert len(results) == 2
    assert results[0] == bindings.CreateTransfersResult(
        index=0,
        result=bindings.CreateTransferResult.LINKED_EVENT_FAILED,
    )
    assert results[1] == bindings.CreateTransfersResult(
        index=1,
        result=bindings.CreateTransferResult.EXISTS_WITH_DIFFERENT_FLAGS,
    )

    accounts = tb_client.lookup_accounts([account_a_id, account_b_id])
    assert len(accounts) == 2

    account_a = accounts[0]
    assert account_a.debits_pending == 0
    assert account_a.debits_posted == 0
    assert account_a.credits_pending == 0
    assert account_a.credits_posted == 0

    account_b = accounts[1]
    assert account_b.debits_pending == 0
    assert account_b.debits_posted == 0
    assert account_b.credits_pending == 0
    assert account_b.credits_posted == 0


def test_create_concurrent_transfers(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
    transfer_a_id: uint128,
    transfer_b_id: uint128,
    concurrency_max: int,
) -> None:
    """Test creating concurrent transfers."""
    # TODO: 1_000_000 don't complete
    transfers_max = 1_000
    account_a = bindings.Account(account_a_id, ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(account_b_id, ledger=uint32(1), code=uint16(2))
    tb_client.create_accounts([account_a, account_b])

    accounts = tb_client.lookup_accounts([account_a_id, account_b_id])
    assert len(accounts) == 2

    account_a_debits = accounts[0].debits_posted
    account_b_credits = accounts[1].credits_posted

    def create_transfer():
        transfer = bindings.Transfer(
            uid.ID(),
            debit_account_id=account_a_id,
            credit_account_id=account_b_id,
            amount=uint64(1),
            ledger=uint32(1),
            code=uint16(1),
        )
        results = tb_client.create_transfers([transfer])
        assert results[0].result == 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency_max) as executor:
        futures = [executor.submit(create_transfer) for _ in range(transfers_max)]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    accounts = tb_client.lookup_accounts([account_a_id, account_b_id])
    assert len(accounts) == 2

    account_a_debits_after = accounts[0].debits_posted
    account_b_credits_after = accounts[1].credits_posted

    assert account_a_debits_after == account_a_debits + transfers_max
    assert account_b_credits_after == account_b_credits + transfers_max


def test_get_account_balances(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
    transfer_a_id: uint128,
) -> None:
    """Test getting account balances."""
    account_a = bindings.Account(
        account_a_id,
        ledger=uint32(1),
        code=uint16(1),
        flags=bindings.AccountFlags(history=True).to_uint16(),
    )
    account_b = bindings.Account(account_b_id, ledger=uint32(1), code=uint16(2))
    tb_client.create_accounts([account_a, account_b])

    transfer_a = bindings.Transfer(
        transfer_a_id,
        debit_account_id=account_a_id,
        credit_account_id=account_b_id,
        amount=uint64(100),
        ledger=uint32(1),
        code=uint16(1),
    )
    tb_client.create_transfers([transfer_a])

    balances = tb_client.get_account_balances(
        bindings.AccountFilter(account_id=account_a_id)
    )

    assert len(balances) == 1

    balance = balances[0]
    assert isinstance(balance, bindings.AccountBalance)
    assert balance.debits_pending == 0
    assert balance.debits_posted == 100
    assert balance.credits_pending == 0
    assert balance.credits_posted == 0
    assert balance.timestamp != 0


def test_get_account_transfers(
    tb_client: Client,
    account_a_id: uint128,
    account_b_id: uint128,
    transfer_a_id: uint128,
    transfer_b_id: uint128,
) -> None:
    """Test getting account transfers."""
    account_a = bindings.Account(account_a_id, ledger=uint32(1), code=uint16(1))
    account_b = bindings.Account(account_b_id, ledger=uint32(1), code=uint16(2))
    tb_client.create_accounts([account_a, account_b])

    transfer_a = bindings.Transfer(
        transfer_a_id,
        debit_account_id=account_a_id,
        credit_account_id=account_b_id,
        amount=uint64(100),
        ledger=uint32(1),
        code=uint16(1),
    )
    transfer_b = bindings.Transfer(
        transfer_b_id,
        debit_account_id=account_b_id,
        credit_account_id=account_a_id,
        amount=uint64(100),
        ledger=uint32(1),
        code=uint16(1),
    )
    tb_client.create_transfers([transfer_a, transfer_b])

    transfers = tb_client.get_account_transfers(
        bindings.AccountFilter(account_id=account_a_id)
    )

    assert len(transfers) == 2

    transfer_a = transfers[0]
    assert isinstance(transfer_a, bindings.Transfer)
    assert transfer_a.id == transfer_a_id
    assert transfer_a.debit_account_id == account_a_id
    assert transfer_a.credit_account_id == account_b_id
    assert transfer_a.amount == 100
    assert transfer_a.ledger == 1
    assert transfer_a.code == 1
    assert transfer_a.pending_id == 0
    assert transfer_a.user_data_128 == 0
    assert transfer_a.user_data_64 == 0
    assert transfer_a.user_data_32 == 0
    assert transfer_a.timeout == 0
    assert transfer_a.flags == 0
    assert transfer_a.timestamp != 0

    transfer_b = transfers[1]
    assert isinstance(transfer_b, bindings.Transfer)
    assert transfer_b.id == transfer_b_id
    assert transfer_b.debit_account_id == account_b_id
    assert transfer_b.credit_account_id == account_a_id
    assert transfer_b.amount == 100
    assert transfer_b.ledger == 1
    assert transfer_b.code == 1
    assert transfer_b.pending_id == 0
    assert transfer_b.user_data_128 == 0
    assert transfer_b.user_data_64 == 0
    assert transfer_b.user_data_32 == 0
    assert transfer_b.timeout == 0
    assert transfer_b.flags == 0
    assert transfer_b.timestamp != 0
