"""Python client for TigerBeetle."""

import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from types import TracebackType
from typing import ClassVar

from tigerbeetle_py._native import tb_client
from tigerbeetle_py._types import bindings, errors, uint

ffi = tb_client.ffi
lib = tb_client.lib


@dataclass(slots=True)
class Request:
    id: int
    packet: ffi.CData
    result: ffi.CData
    ready: threading.Event


def handle_exception(
    exception: type[BaseException],
    exception_value: BaseException,
    traceback: TracebackType,
) -> None:
    """Handle exceptions raised in the Zig client thread.

    See [1] on why exceptions cannot be propagated there and have to be
    re-raised here.

    [1]: https://cffi.readthedocs.io/en/latest/using.html#extern-python-reference
    """
    raise exception_value.with_traceback(traceback)


@ffi.def_extern(onerror=handle_exception)
def on_completion_fn(context, client, packet, result_ptr, result_len):
    """
    Simple statically registered extern "Python" fn. This gets
    called for any callbacks, looks up the respective client from our
    global mapping, and forwards on the callback.

    NB: This runs in the Zig client thread.
    """
    _on_completion_fn(context, client, packet, result_ptr, result_len)


def _on_completion_fn(
    context: ffi.CData,
    client: ffi.CData,
    packet: ffi.CData,
    result_ptr: ffi.CData,
    result_len: ffi.CData,
) -> None:
    req = Client.inflight[int(ffi.cast("int", packet[0].user_data))]
    if req.packet != packet:
        raise Exception("Packet mismatch")

    if result_len > 0 and result_ptr is not None:
        op = bindings.Operation(int(packet.operation))
        result_size = get_result_size(op)
        if result_len % result_size != 0:
            raise Exception("Invalid result length")

        if (
            op != lib.TB_OPERATION_GET_ACCOUNT_TRANSFERS
            and op != lib.TB_OPERATION_GET_ACCOUNT_BALANCES
        ):
            # Make sure the amount of results at least matches the amount of requests.
            count = packet.data_size // get_event_size(op)
            if count * result_size < result_len:
                raise Exception("Invalid result length")

    req.result = result_ptr
    req.packet.data_size = result_len
    req.ready.set()


def cint128_to_int(x: ffi.CData) -> uint.UInt128:
    return uint.UInt128.from_tuple(x.high, x.low)


def get_event_size(op: bindings.Operation) -> int:
    return {
        lib.TB_OPERATION_CREATE_ACCOUNTS: ffi.sizeof("tb_account_t"),
        lib.TB_OPERATION_CREATE_TRANSFERS: ffi.sizeof("tb_transfer_t"),
        lib.TB_OPERATION_LOOKUP_ACCOUNTS: ffi.sizeof("tb_uint128_t"),
        lib.TB_OPERATION_LOOKUP_TRANSFERS: ffi.sizeof("tb_uint128_t"),
        lib.TB_OPERATION_GET_ACCOUNT_TRANSFERS: ffi.sizeof("tb_account_filter_t"),
        lib.TB_OPERATION_GET_ACCOUNT_BALANCES: ffi.sizeof("tb_account_filter_t"),
    }.get(op, 0)


def get_result_size(op: bindings.Operation) -> int:
    return {
        lib.TB_OPERATION_CREATE_ACCOUNTS: ffi.sizeof("tb_create_accounts_result_t"),
        lib.TB_OPERATION_CREATE_TRANSFERS: ffi.sizeof("tb_create_transfers_result_t"),
        lib.TB_OPERATION_LOOKUP_ACCOUNTS: ffi.sizeof("tb_account_t"),
        lib.TB_OPERATION_LOOKUP_TRANSFERS: ffi.sizeof("tb_transfer_t"),
        lib.TB_OPERATION_GET_ACCOUNT_TRANSFERS: ffi.sizeof("tb_account_t"),
        lib.TB_OPERATION_GET_ACCOUNT_BALANCES: ffi.sizeof("tb_account_balance_t"),
    }.get(op, 0)


@contextmanager
def request_ctx(c: ffi.CData, packet: ffi.CData | None = None) -> Iterator[Request]:
    if packet is None:
        packet = ffi.new("tb_packet_t *")

    status = lib.tb_client_acquire_packet(
        c[0],
        ffi.new("tb_packet_t * *", packet),
    )
    if status == lib.TB_STATUS_CONCURRENCY_MAX_INVALID:
        raise errors.ConcurrencyExceededError()
    if status == lib.TB_PACKET_ACQUIRE_SHUTDOWN:
        raise errors.ClientClosedError()
    if packet is None:
        raise errors.TigerBeetleError("Unexpected None packet")

    req = Request(
        id=uuid.uuid4().int & 0x7FFFFFFF,
        packet=packet,
        result=None,
        ready=threading.Event(),
    )

    try:
        yield req
    finally:
        # Release packet for other threads to use
        lib.tb_client_release_packet(c[0], packet)
        del Client.inflight[req.id]


# TODO: ensure endianness is correct
class Client:
    """Client for TigerBeetle."""

    inflight: ClassVar[dict[int, Request]] = {}

    def __init__(
        self,
        cluster_id: uint.UInt128,
        addresses: list[str],
        concurrency_max: int,
    ) -> None:
        self._tb_client: ffi.CData | None = ffi.new("tb_client_t *")
        addresses_raw = ",".join(addresses).encode()
        status = lib.tb_client_init(
            self._tb_client,
            cluster_id.tuple,
            ffi.new("char[]", addresses_raw),
            len(addresses_raw),
            concurrency_max,
            0,
            lib.on_completion_fn,
        )

        if status != lib.TB_STATUS_SUCCESS:
            self._raise_status(status)

    @staticmethod
    def _raise_status(status: int) -> None:
        match status:
            case lib.TB_STATUS_UNEXPECTED:
                raise errors.UnexpectedError()
            case lib.TB_STATUS_OUT_OF_MEMORY:
                raise errors.OutOfMemoryError()
            case lib.TB_STATUS_ADDRESS_INVALID:
                raise errors.InvalidAddressError()
            case lib.TB_STATUS_ADDRESS_LIMIT_EXCEEDED:
                raise errors.AddressLimitExceededError()
            case lib.TB_STATUS_CONCURRENCY_MAX_INVALID:
                raise errors.InvalidConcurrencyMaxError()
            case lib.TB_STATUS_SYSTEM_RESOURCES:
                raise errors.SystemResourcesError()
            case lib.TB_STATUS_NETWORK_SUBSYSTEM:
                raise errors.NetworkSubsystemError()
            case _:
                msg = f"Unexpected status: {status}"
                raise errors.TigerBeetleError(msg)

    def _do_request(
        self,
        op: bindings.Operation,
        count: int,
        data: ffi.CData,
        result_type: str,
    ) -> int:
        if count == 0:
            raise errors.EmptyBatchError()

        if self._tb_client is None:
            raise errors.ClientClosedError()

        with request_ctx(self._tb_client) as req:
            req.packet.user_data = ffi.cast("void *", req.id)
            req.packet.operation = ffi.cast("TB_OPERATION", op.value)
            req.packet.status = lib.TB_PACKET_OK
            req.packet.data_size = count * get_event_size(op)
            req.packet.data = data

            Client.inflight[req.id] = req

            # Submit the request.
            lib.tb_client_submit(self._tb_client[0], req.packet)

            # Wait for the response
            req.ready.wait()

            status = int(ffi.cast("TB_PACKET_STATUS", req.packet.status))
            if status != lib.TB_PACKET_OK:
                match status:
                    case lib.TB_PACKET_TOO_MUCH_DATA:
                        raise errors.MaximumBatchSizeExceededError()
                    case lib.TB_PACKET_INVALID_OPERATION:
                        # we control what lib.TB_OPERATION is given
                        # but allow an invalid opcode to be passed to emulate a client nop
                        raise errors.InvalidOperationError()
                    case lib.TB_PACKET_INVALID_DATA_SIZE:
                        # we control what type of data is given
                        raise Exception("unreachable")
                    case _:
                        raise Exception(
                            "tb_client_submit(): returned packet with invalid status"
                        )

            result_count = req.packet.data_size // get_result_size(op)
            return ffi.cast(result_type.format(count=result_count), req.result)

    def close(self) -> None:
        if self._tb_client is not None:
            lib.tb_client_deinit(self._tb_client[0])
            self._tb_client = None

    def create_accounts(
        self,
        accounts: list[bindings.Account],
    ) -> list[bindings.CreateAccountsResult]:
        """Create accounts in the ledger.

        Args:
            accounts: List of accounts to create.

        Returns:
            List of account creation results.
        """
        count = len(accounts)

        batch = ffi.new("tb_account_t[]", count)
        for idx, account in enumerate(accounts):
            batch[idx].id = account.id.tuple
            batch[idx].ledger = account.ledger.int
            batch[idx].code = account.code.int
            batch[idx].flags = account.flags.int
            batch[idx].user_data_128 = account.user_data_128.tuple
            batch[idx].user_data_64 = account.user_data_64.int
            batch[idx].user_data_32 = account.user_data_32.int
            batch[idx].timestamp = 0

        results = self._do_request(
            bindings.Operation.CREATE_ACCOUNTS,
            count,
            batch,
            "tb_create_accounts_result_t[{count}]",
        )
        results_by_idx = {result.index: result for result in results}

        return [
            bindings.CreateAccountsResult(
                results_by_idx[idx].index,
                bindings.CreateAccountResult(results_by_idx[idx].result),
            )
            if idx in results_by_idx
            else bindings.CreateAccountsResult(
                idx,
                bindings.CreateAccountResult(bindings.CreateAccountResult.OK),
            )
            for idx in range(count)
        ]

    def create_transfers(
        self,
        transfers: list[bindings.Transfer],
    ) -> list[bindings.CreateTransfersResult]:
        """Create transfers in the ledger.

        Args:
            transfers: List of transfers to create.

        Returns:
            List of transfer creation results.
        """
        count = len(transfers)
        # results = ffi.new("tb_create_transfers_result_t[]", count)

        batch = ffi.new("tb_transfer_t[]", count)
        for idx, transfer in enumerate(transfers):
            batch[idx].id = transfer.id.tuple
            batch[idx].debit_account_id = transfer.debit_account_id.tuple
            batch[idx].credit_account_id = transfer.credit_account_id.tuple
            batch[idx].amount = transfer.amount.tuple
            batch[idx].pending_id = transfer.pending_id.tuple
            batch[idx].user_data_128 = transfer.user_data_128.tuple
            batch[idx].user_data_64 = transfer.user_data_64.int
            batch[idx].user_data_32 = transfer.user_data_32.int
            batch[idx].timeout = transfer.timeout.int
            batch[idx].ledger = transfer.ledger.int
            batch[idx].code = transfer.code.int
            batch[idx].flags = transfer.flags.int
            batch[idx].timestamp = 0

        results = self._do_request(
            bindings.Operation.CREATE_TRANSFERS,
            count,
            batch,
            "tb_create_transfers_result_t[{count}]",
        )
        results_by_idx = {result.index: result for result in results}

        return [
            bindings.CreateTransfersResult(
                results_by_idx[idx].index,
                bindings.CreateTransferResult(results_by_idx[idx].result),
            )
            if idx in results_by_idx
            else bindings.CreateTransfersResult(
                idx,
                bindings.CreateTransferResult(bindings.CreateTransferResult.OK),
            )
            for idx in range(count)
        ]

    def lookup_accounts(
        self,
        account_ids: list[uint.UInt128],
    ) -> list[bindings.Account]:
        """Lookup accounts in the ledger.

        Args:
            account_ids: List of account IDs to look up.

        Returns:
            List of account dictionaries.
        """
        count = len(account_ids)
        batch = ffi.new("tb_uint128_t[]", [i.tuple for i in account_ids])

        results = self._do_request(
            bindings.Operation.LOOKUP_ACCOUNTS,
            count,
            batch,
            "tb_account_t[{count}]",
        )

        return [
            bindings.Account(
                id=cint128_to_int(result.id),
                debits_pending=cint128_to_int(result.debits_pending),
                debits_posted=cint128_to_int(result.debits_posted),
                credits_pending=cint128_to_int(result.credits_pending),
                credits_posted=cint128_to_int(result.credits_posted),
                user_data_128=cint128_to_int(result.user_data_128),
                user_data_64=uint.UInt64(result.user_data_64),
                user_data_32=uint.UInt32(result.user_data_32),
                ledger=uint.UInt32(result.ledger),
                code=uint.UInt16(result.code),
                flags=uint.UInt16(result.flags),
                timestamp=uint.UInt64(result.timestamp),
                reserved=result.reserved,
            )
            for result in results
        ]

    def lookup_transfers(
        self,
        transfer_ids: list[uint.UInt128],
    ) -> list[bindings.Transfer]:
        """Lookup transfers in the ledger.

        Args:
            transfer_ids: List of transfer IDs to look up.

        Returns:
            List of transfer dictionaries.
        """
        count = len(transfer_ids)
        batch = ffi.new("tb_uint128_t[]", [i.tuple for i in transfer_ids])

        results = self._do_request(
            bindings.Operation.LOOKUP_TRANSFERS,
            count,
            batch,
            "tb_transfer_t[{count}]",
        )

        return [
            bindings.Transfer(
                id=cint128_to_int(result.id),
                debit_account_id=cint128_to_int(result.debit_account_id),
                credit_account_id=cint128_to_int(result.credit_account_id),
                amount=cint128_to_int(result.amount),
                pending_id=cint128_to_int(result.pending_id),
                user_data_128=cint128_to_int(result.user_data_128),
                user_data_64=uint.UInt64(result.user_data_64),
                user_data_32=uint.UInt32(result.user_data_32),
                timeout=uint.UInt32(result.timeout),
                ledger=uint.UInt32(result.ledger),
                code=uint.UInt16(result.code),
                flags=uint.UInt16(result.flags),
                timestamp=uint.UInt64(result.timestamp),
            )
            for result in results
        ]

    def get_account_transfers(
        self,
        filt: bindings.AccountFilter,
    ) -> list[bindings.Transfer]:
        """Get transfers for an account.

        Args:
            filt: The query filter.

        Returns:
            List of transfers.
        """
        batch = ffi.new("tb_account_filter_t[]", 1)

        batch[0].account_id = filt.account_id.tuple
        batch[0].timestamp_min = filt.timestamp_min.int
        batch[0].timestamp_max = filt.timestamp_max.int
        batch[0].limit = filt.limit.int
        batch[0].flags = filt.flags.int

        results = self._do_request(
            bindings.Operation.GET_ACCOUNT_TRANSFERS,
            1,
            batch,
            "tb_transfer_t[{count}]",
        )

        return [
            bindings.Transfer(
                id=cint128_to_int(result.id),
                debit_account_id=cint128_to_int(result.debit_account_id),
                credit_account_id=cint128_to_int(result.credit_account_id),
                amount=cint128_to_int(result.amount),
                pending_id=cint128_to_int(result.pending_id),
                user_data_128=cint128_to_int(result.user_data_128),
                user_data_64=uint.UInt64(result.user_data_64),
                user_data_32=uint.UInt32(result.user_data_32),
                timeout=uint.UInt32(result.timeout),
                ledger=uint.UInt32(result.ledger),
                code=uint.UInt16(result.code),
                flags=uint.UInt16(result.flags),
                timestamp=uint.UInt64(result.timestamp),
            )
            for result in results
        ]

    def get_account_balances(
        self,
        filt: bindings.AccountFilter,
    ) -> list[bindings.AccountBalance]:
        """Get balances for an account.

        Args:
            filt: The query filter.

        Returns:
            List of account balances.
        """
        batch = ffi.new("tb_account_filter_t[]", 1)

        batch[0].account_id = filt.account_id.tuple
        batch[0].timestamp_min = filt.timestamp_min.int
        batch[0].timestamp_max = filt.timestamp_max.int
        batch[0].limit = filt.limit.int
        batch[0].flags = filt.flags.int

        results = self._do_request(
            bindings.Operation.GET_ACCOUNT_BALANCES,
            1,
            batch,
            "tb_account_balance_t[{count}]",
        )

        return [
            bindings.AccountBalance(
                debits_pending=cint128_to_int(result.debits_pending),
                debits_posted=cint128_to_int(result.debits_posted),
                credits_pending=cint128_to_int(result.credits_pending),
                credits_posted=cint128_to_int(result.credits_posted),
                timestamp=uint.UInt64(result.timestamp),
            )
            for result in results
        ]
