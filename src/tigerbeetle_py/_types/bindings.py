"""Bindings for the TigerBeetle types."""

import enum
from dataclasses import dataclass

from tigerbeetle_py._types import uint


@dataclass(slots=True, frozen=True)
class AccountFlags:
    """See [AccountFlags](https://docs.tigerbeetle.com/reference/account#flags)"""

    linked: bool = False
    """See [linked](https://docs.tigerbeetle.com/reference/account#flagslinked)"""
    debits_must_not_exceed_credits: bool = False
    """See [debits_must_not_exceed_credits](https://docs.tigerbeetle.com/reference/account#flagsdebits_must_not_exceed_credits)"""
    credits_must_not_exceed_debits: bool = False
    """See [credits_must_not_exceed_debits](https://docs.tigerbeetle.com/reference/account#flagscredits_must_not_exceed_debits)"""
    history: bool = False
    """See [history](https://docs.tigerbeetle.com/reference/account#flagshistory)"""

    def to_uint16(self) -> uint.UInt16:
        """Convert to a `UInt16`."""
        return uint.UInt16(
            (self.linked << 0)
            | (self.debits_must_not_exceed_credits << 1)
            | (self.credits_must_not_exceed_debits << 2)
            | (self.history << 3)
        )


@dataclass(slots=True, frozen=True)
class TransferFlags:
    """See [TransferFlags](https://docs.tigerbeetle.com/reference/transfer#flags)"""

    linked: bool = False
    """See [linked](https://docs.tigerbeetle.com/reference/transfer#flagslinked)"""
    pending: bool = False
    """See [pending](https://docs.tigerbeetle.com/reference/transfer#flagspending)"""
    post_pending_transfer: bool = False
    """See [post_pending_transfer](https://docs.tigerbeetle.com/reference/transfer#flagspost_pending_transfer)"""
    void_pending_transfer: bool = False
    """See [void_pending_transfer](https://docs.tigerbeetle.com/reference/transfer#flagsvoid_pending_transfer)"""
    balancing_debit: bool = False
    """See [balancing_debit](https://docs.tigerbeetle.com/reference/transfer#flagsbalancing_debit)"""
    balancing_credit: bool = False
    """See [balancing_credit](https://docs.tigerbeetle.com/reference/transfer#flagsbalancing_credit)"""

    def to_uint16(self) -> uint.UInt16:
        """Convert to a `UInt16`."""
        return uint.UInt16(
            (self.linked << 0)
            | (self.pending << 1)
            | (self.post_pending_transfer << 2)
            | (self.void_pending_transfer << 3)
            | (self.balancing_debit << 4)
            | (self.balancing_credit << 5)
        )


@dataclass(slots=True, frozen=True)
class AccountFilterFlags:
    """See [AccountFilterFlags](https://docs.tigerbeetle.com/reference/account-filter#flags)"""

    debits: bool = False
    """See [debits](https://docs.tigerbeetle.com/reference/account-filter#flagsdebits)"""
    credits: bool = False
    """See [credits](https://docs.tigerbeetle.com/reference/account-filter#flagscredits)"""
    reversed: bool = False
    """See [reversed](https://docs.tigerbeetle.com/reference/account-filter#flagsreversed)"""

    def to_uint32(self) -> uint.UInt32:
        """Convert to a `UInt32`."""
        return uint.UInt32(
            (self.debits << 0) | (self.credits << 1) | (self.reversed << 2)
        )


@dataclass(slots=True, frozen=True)
class Account:
    """See [Account](https://docs.tigerbeetle.com/reference/account/#)"""

    id: uint.UInt128
    """See [id](https://docs.tigerbeetle.com/reference/account/#id)"""
    ledger: uint.UInt32
    """See [ledger](https://docs.tigerbeetle.com/reference/account/#ledger)"""
    code: uint.UInt16
    """See [code](https://docs.tigerbeetle.com/reference/account/#code)"""
    debits_pending: uint.UInt128 = uint.UInt128(0)
    """See [debits_pending](https://docs.tigerbeetle.com/reference/account/#debits_pending)"""
    debits_posted: uint.UInt128 = uint.UInt128(0)
    """See [debits_posted](https://docs.tigerbeetle.com/reference/account/#debits_posted)"""
    credits_pending: uint.UInt128 = uint.UInt128(0)
    """See [credits_pending](https://docs.tigerbeetle.com/reference/account/#credits_pending)"""
    credits_pending: uint.UInt128 = uint.UInt128(0)
    """See [credits_posted](https://docs.tigerbeetle.com/reference/account/#credits_posted)"""
    user_data_128: uint.UInt128 = uint.UInt128(0)
    """See [user_data_128](https://docs.tigerbeetle.com/reference/account/#user_data_128)"""
    user_data_64: uint.UInt64 = uint.UInt64(0)
    """See [user_data_64](https://docs.tigerbeetle.com/reference/account/#user_data_64)"""
    user_data_32: uint.UInt32 = uint.UInt32(0)
    """See [user_data_32](https://docs.tigerbeetle.com/reference/account/#user_data_32)"""
    flags: uint.UInt16 = AccountFlags().to_uint16()
    """See [flags](https://docs.tigerbeetle.com/reference/account/#flags)"""
    timestamp: uint.UInt64 = uint.UInt64(0)
    """See [timestamp](https://docs.tigerbeetle.com/reference/account/#timestamp)"""
    reserved: int = 0
    """See [reserved](https://docs.tigerbeetle.com/reference/account/#reserved)"""

    def get_flags(self) -> AccountFlags:
        """Get the account flags."""
        return AccountFlags(
            linked=bool((self.flags >> 0) & 0x1),
            debits_must_not_exceed_credits=bool((self.flags >> 1) & 0x1),
            credits_must_not_exceed_debits=bool((self.flags >> 2) & 0x1),
            history=bool((self.flags >> 3) & 0x1),
        )


@dataclass(slots=True, frozen=True)
class Transfer:
    """See [Transfer](https://docs.tigerbeetle.com/reference/transfer/#)"""

    id: uint.UInt128
    """See [id](https://docs.tigerbeetle.com/reference/transfer/#id)"""
    debit_account_id: uint.UInt128
    """See [debit_account_id](https://docs.tigerbeetle.com/reference/transfer/#debit_account_id)"""
    credit_account_id: uint.UInt128
    """See [credit_account_id](https://docs.tigerbeetle.com/reference/transfer/#credit_account_id)"""
    amount: uint.UInt128
    """See [amount](https://docs.tigerbeetle.com/reference/transfer/#amount)"""
    ledger: uint.UInt32
    """See [ledger](https://docs.tigerbeetle.com/reference/transfer/#ledger)"""
    code: uint.UInt16
    """See [code](https://docs.tigerbeetle.com/reference/transfer/#code)"""
    pending_id: uint.UInt128 = uint.UInt128(0)
    """See [pending_id](https://docs.tigerbeetle.com/reference/transfer/#pending_id)"""
    user_data_128: uint.UInt128 = uint.UInt128(0)
    """See [user_data_128](https://docs.tigerbeetle.com/reference/transfer/#user_data_128)"""
    user_data_64: uint.UInt64 = uint.UInt64(0)
    """See [user_data_64](https://docs.tigerbeetle.com/reference/transfer/#user_data_64)"""
    user_data_32: uint.UInt32 = uint.UInt32(0)
    """See [user_data_32](https://docs.tigerbeetle.com/reference/transfer/#user_data_32)"""
    timeout: uint.UInt32 = uint.UInt32(0)
    """See [timeout](https://docs.tigerbeetle.com/reference/transfer/#timeout)"""
    flags: uint.UInt16 = TransferFlags().to_uint16()
    """See [flags](https://docs.tigerbeetle.com/reference/transfer/#flags)"""
    timestamp: uint.UInt64 = uint.UInt64(0)
    """See [timestamp](https://docs.tigerbeetle.com/reference/transfer/#timestamp)"""

    def get_flags(self) -> TransferFlags:
        """Get the transfer flags."""
        return TransferFlags(
            linked=bool((self.flags >> 0) & 0x1),
            pending=bool((self.flags >> 1) & 0x1),
            post_pending_transfer=bool((self.flags >> 2) & 0x1),
            void_pending_transfer=bool((self.flags >> 3) & 0x1),
            balancing_debit=bool((self.flags >> 4) & 0x1),
            balancing_credit=bool((self.flags >> 5) & 0x1),
        )


class CreateAccountResult(enum.IntEnum):
    """See [CreateAccountResult](https://docs.tigerbeetle.com/reference/requests/create_accounts#)"""

    OK = 0
    """See [ok](https://docs.tigerbeetle.com/reference/requests/create_accounts#ok)"""
    LINKED_EVENT_FAILED = 1
    """See [linked_event_failed](https://docs.tigerbeetle.com/reference/requests/create_accounts#linked_event_failed)"""
    LINKED_EVENT_CHAIN_OPEN = 2
    """See [linked_event_chain_open](https://docs.tigerbeetle.com/reference/requests/create_accounts#linked_event_chain_open)"""
    TIMESTAMP_MUST_BE_ZERO = 3
    """See [timestamp_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#timestamp_must_be_zero)"""
    RESERVED_FIELD = 4
    """See [reserved_field](https://docs.tigerbeetle.com/reference/requests/create_accounts#reserved_field)"""
    RESERVED_FLAG = 5
    """See [reserved_flag](https://docs.tigerbeetle.com/reference/requests/create_accounts#reserved_flag)"""
    ID_MUST_NOT_BE_ZERO = 6
    """See [id_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#id_must_not_be_zero)"""
    ID_MUST_NOT_BE_INT_MAX = 7
    """See [id_must_not_be_int_max](https://docs.tigerbeetle.com/reference/requests/create_accounts#id_must_not_be_int_max)"""
    FLAGS_ARE_MUTUALLY_EXCLUSIVE = 8
    """See [flags_are_mutually_exclusive](https://docs.tigerbeetle.com/reference/requests/create_accounts#flags_are_mutually_exclusive)"""
    DEBITS_PENDING_MUST_BE_ZERO = 9
    """See [debits_pending_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#debits_pending_must_be_zero)"""
    DEBITS_POSTED_MUST_BE_ZERO = 10
    """See [debits_posted_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#debits_posted_must_be_zero)"""
    CREDITS_PENDING_MUST_BE_ZERO = 11
    """See [credits_pending_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#credits_pending_must_be_zero)"""
    CREDITS_POSTED_MUST_BE_ZERO = 12
    """See [credits_posted_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#credits_posted_must_be_zero)"""
    LEDGER_MUST_NOT_BE_ZERO = 13
    """See [ledger_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#ledger_must_not_be_zero)"""
    CODE_MUST_NOT_BE_ZERO = 14
    """See [code_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_accounts#code_must_not_be_zero)"""
    EXISTS_WITH_DIFFERENT_FLAGS = 15
    """See [exists_with_different_flags](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists_with_different_flags)"""
    EXISTS_WITH_DIFFERENT_USER_DATA_128 = 16
    """See [exists_with_different_user_data_128](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists_with_different_user_data_128)"""
    EXISTS_WITH_DIFFERENT_USER_DATA_64 = 17
    """See [exists_with_different_user_data_64](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists_with_different_user_data_64)"""
    EXISTS_WITH_DIFFERENT_USER_DATA_32 = 18
    """See [exists_with_different_user_data_32](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists_with_different_user_data_32)"""
    EXISTS_WITH_DIFFERENT_LEDGER = 19
    """See [exists_with_different_ledger](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists_with_different_ledger)"""
    EXISTS_WITH_DIFFERENT_CODE = 20
    """See [exists_with_different_code](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists_with_different_code)"""
    EXISTS = 21
    """See [exists](https://docs.tigerbeetle.com/reference/requests/create_accounts#exists)"""


class CreateTransferResult(enum.IntEnum):
    """See [CreateTransferResult](https://docs.tigerbeetle.com/reference/requests/create_transfers#)"""

    OK = 0
    """See [ok](https://docs.tigerbeetle.com/reference/requests/create_transfers#ok)"""
    LINKED_EVENT_FAILED = 1
    """See [linked_event_failed](https://docs.tigerbeetle.com/reference/requests/create_transfers#linked_event_failed)"""
    LINKED_EVENT_CHAIN_OPEN = 2
    """See [linked_event_chain_open](https://docs.tigerbeetle.com/reference/requests/create_transfers#linked_event_chain_open)"""
    TIMESTAMP_MUST_BE_ZERO = 3
    """See [timestamp_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#timestamp_must_be_zero)"""
    RESERVED_FLAG = 4
    """See [reserved_flag](https://docs.tigerbeetle.com/reference/requests/create_transfers#reserved_flag)"""
    ID_MUST_NOT_BE_ZERO = 5
    """See [id_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#id_must_not_be_zero)"""
    ID_MUST_NOT_BE_INT_MAX = 6
    """See [id_must_not_be_int_max](https://docs.tigerbeetle.com/reference/requests/create_transfers#id_must_not_be_int_max)"""
    FLAGS_ARE_MUTUALLY_EXCLUSIVE = 7
    """See [flags_are_mutually_exclusive](https://docs.tigerbeetle.com/reference/requests/create_transfers#flags_are_mutually_exclusive)"""
    DEBIT_ACCOUNT_ID_MUST_NOT_BE_ZERO = 8
    """See [debit_account_id_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#debit_account_id_must_not_be_zero)"""
    DEBIT_ACCOUNT_ID_MUST_NOT_BE_INT_MAX = 9
    """See [debit_account_id_must_not_be_int_max](https://docs.tigerbeetle.com/reference/requests/create_transfers#debit_account_id_must_not_be_int_max)"""
    CREDIT_ACCOUNT_ID_MUST_NOT_BE_ZERO = 10
    """See [credit_account_id_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#credit_account_id_must_not_be_zero)"""
    CREDIT_ACCOUNT_ID_MUST_NOT_BE_INT_MAX = 11
    """See [credit_account_id_must_not_be_int_max](https://docs.tigerbeetle.com/reference/requests/create_transfers#credit_account_id_must_not_be_int_max)"""
    ACCOUNTS_MUST_BE_DIFFERENT = 12
    """See [accounts_must_be_different](https://docs.tigerbeetle.com/reference/requests/create_transfers#accounts_must_be_different)"""
    PENDING_ID_MUST_BE_ZERO = 13
    """See [pending_id_must_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_id_must_be_zero)"""
    PENDING_ID_MUST_NOT_BE_ZERO = 14
    """See [pending_id_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_id_must_not_be_zero)"""
    PENDING_ID_MUST_NOT_BE_INT_MAX = 15
    """See [pending_id_must_not_be_int_max](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_id_must_not_be_int_max)"""
    PENDING_ID_MUST_BE_DIFFERENT = 16
    """See [pending_id_must_be_different](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_id_must_be_different)"""
    TIMEOUT_RESERVED_FOR_PENDING_TRANSFER = 17
    """See [timeout_reserved_for_pending_transfer](https://docs.tigerbeetle.com/reference/requests/create_transfers#timeout_reserved_for_pending_transfer)"""
    AMOUNT_MUST_NOT_BE_ZERO = 18
    """See [amount_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#amount_must_not_be_zero)"""
    LEDGER_MUST_NOT_BE_ZERO = 19
    """See [ledger_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#ledger_must_not_be_zero)"""
    CODE_MUST_NOT_BE_ZERO = 20
    """See [code_must_not_be_zero](https://docs.tigerbeetle.com/reference/requests/create_transfers#code_must_not_be_zero)"""
    DEBIT_ACCOUNT_NOT_FOUND = 21
    """See [debit_account_not_found](https://docs.tigerbeetle.com/reference/requests/create_transfers#debit_account_not_found)"""
    CREDIT_ACCOUNT_NOT_FOUND = 22
    """See [credit_account_not_found](https://docs.tigerbeetle.com/reference/requests/create_transfers#credit_account_not_found)"""
    ACCOUNTS_MUST_HAVE_THE_SAME_LEDGER = 23
    """See [accounts_must_have_the_same_ledger](https://docs.tigerbeetle.com/reference/requests/create_transfers#accounts_must_have_the_same_ledger)"""
    TRANSFER_MUST_HAVE_THE_SAME_LEDGER_AS_ACCOUNTS = 24
    """See [transfer_must_have_the_same_ledger_as_accounts](https://docs.tigerbeetle.com/reference/requests/create_transfers#transfer_must_have_the_same_ledger_as_accounts)"""
    PENDING_TRANSFER_NOT_FOUND = 25
    """See [pending_transfer_not_found](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_not_found)"""
    PENDING_TRANSFER_NOT_PENDING = 26
    """See [pending_transfer_not_pending](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_not_pending)"""
    PENDING_TRANSFER_HAS_DIFFERENT_DEBIT_ACCOUNT_ID = 27
    """See [pending_transfer_has_different_debit_account_id](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_has_different_debit_account_id)"""
    PENDING_TRANSFER_HAS_DIFFERENT_CREDIT_ACCOUNT_ID = 28
    """See [pending_transfer_has_different_credit_account_id](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_has_different_credit_account_id)"""
    PENDING_TRANSFER_HAS_DIFFERENT_LEDGER = 29
    """See [pending_transfer_has_different_ledger](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_has_different_ledger)"""
    PENDING_TRANSFER_HAS_DIFFERENT_CODE = 30
    """See [pending_transfer_has_different_code](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_has_different_code)"""
    EXCEEDS_PENDING_TRANSFER_AMOUNT = 31
    """See [exceeds_pending_transfer_amount](https://docs.tigerbeetle.com/reference/requests/create_transfers#exceeds_pending_transfer_amount)"""
    PENDING_TRANSFER_HAS_DIFFERENT_AMOUNT = 32
    """See [pending_transfer_has_different_amount](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_has_different_amount)"""
    PENDING_TRANSFER_ALREADY_POSTED = 33
    """See [pending_transfer_already_posted](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_already_posted)"""
    PENDING_TRANSFER_ALREADY_VOIDED = 34
    """See [pending_transfer_already_voided](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_already_voided)"""
    PENDING_TRANSFER_EXPIRED = 35
    """See [pending_transfer_expired](https://docs.tigerbeetle.com/reference/requests/create_transfers#pending_transfer_expired)"""
    EXISTS_WITH_DIFFERENT_FLAGS = 36
    """See [exists_with_different_flags](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_flags)"""
    EXISTS_WITH_DIFFERENT_DEBIT_ACCOUNT_ID = 37
    """See [exists_with_different_debit_account_id](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_debit_account_id)"""
    EXISTS_WITH_DIFFERENT_CREDIT_ACCOUNT_ID = 38
    """See [exists_with_different_credit_account_id](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_credit_account_id)"""
    EXISTS_WITH_DIFFERENT_AMOUNT = 39
    """See [exists_with_different_amount](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_amount)"""
    EXISTS_WITH_DIFFERENT_PENDING_ID = 40
    """See [exists_with_different_pending_id](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_pending_id)"""
    EXISTS_WITH_DIFFERENT_USER_DATA_128 = 41
    """See [exists_with_different_user_data_128](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_user_data_128)"""
    EXISTS_WITH_DIFFERENT_USER_DATA_64 = 42
    """See [exists_with_different_user_data_64](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_user_data_64)"""
    EXISTS_WITH_DIFFERENT_USER_DATA_32 = 43
    """See [exists_with_different_user_data_32](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_user_data_32)"""
    EXISTS_WITH_DIFFERENT_TIMEOUT = 44
    """See [exists_with_different_timeout](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_timeout)"""
    EXISTS_WITH_DIFFERENT_CODE = 45
    """See [exists_with_different_code](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists_with_different_code)"""
    EXISTS = 46
    """See [exists](https://docs.tigerbeetle.com/reference/requests/create_transfers#exists)"""
    OVERFLOWS_DEBITS_PENDING = 47
    """See [overflows_debits_pending](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_debits_pending)"""
    OVERFLOWS_CREDITS_PENDING = 48
    """See [overflows_credits_pending](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_credits_pending)"""
    OVERFLOWS_DEBITS_POSTED = 49
    """See [overflows_debits_posted](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_debits_posted)"""
    OVERFLOWS_CREDITS_POSTED = 50
    """See [overflows_credits_posted](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_credits_posted)"""
    OVERFLOWS_DEBITS = 51
    """See [overflows_debits](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_debits)"""
    OVERFLOWS_CREDITS = 52
    """See [overflows_credits](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_credits)"""
    OVERFLOWS_TIMEOUT = 53
    """See [overflows_timeout](https://docs.tigerbeetle.com/reference/requests/create_transfers#overflows_timeout)"""
    EXCEEDS_CREDITS = 54
    """See [exceeds_credits](https://docs.tigerbeetle.com/reference/requests/create_transfers#exceeds_credits)"""
    EXCEEDS_DEBITS = 55
    """See [exceeds_debits](https://docs.tigerbeetle.com/reference/requests/create_transfers#exceeds_debits)"""


@dataclass(slots=True, frozen=True)
class CreateAccountsResult:
    """Create accounts result."""

    index: int
    result: CreateAccountResult


@dataclass(slots=True, frozen=True)
class CreateTransfersResult:
    """Create transfers result."""

    index: int
    result: CreateTransferResult


@dataclass(slots=True, frozen=True)
class AccountFilter:
    """See [AccountFilter](https://docs.tigerbeetle.com/reference/account-filter#)"""

    account_id: uint.UInt128
    """See [account_id](https://docs.tigerbeetle.com/reference/account-filter#account_id)"""
    timestamp_min: uint.UInt64 = uint.UInt64(0)
    """See [timestamp_min](https://docs.tigerbeetle.com/reference/account-filter#timestamp_min)"""
    timestamp_max: uint.UInt64 = uint.UInt64(0)
    """See [timestamp_max](https://docs.tigerbeetle.com/reference/account-filter#timestamp_max)"""
    limit: uint.UInt32 = uint.UInt32(100)
    """See [limit](https://docs.tigerbeetle.com/reference/account-filter#limit)"""
    flags: uint.UInt32 = AccountFilterFlags().to_uint32()
    """See [flags](https://docs.tigerbeetle.com/reference/account-filter#flags)"""

    def get_flags(self) -> AccountFilterFlags:
        """Get the account filter flags."""
        return AccountFilterFlags(
            debits=bool((self.flags >> 0) & 0x1),
            credits=bool((self.flags >> 1) & 0x1),
            reversed=bool((self.flags >> 2) & 0x1),
        )


@dataclass(slots=True, frozen=True)
class AccountBalance:
    """See [AccountBalance](https://docs.tigerbeetle.com/reference/account-balances#)"""

    debits_pending: uint.UInt128
    """See [debits_pending](https://docs.tigerbeetle.com/reference/account-balances#debits_pending)"""
    debits_posted: uint.UInt128
    """See [debits_posted](https://docs.tigerbeetle.com/reference/account-balances#debits_posted)"""
    credits_pending: uint.UInt128
    """See [credits_pending](https://docs.tigerbeetle.com/reference/account-balances#credits_pending)"""
    credits_posted: uint.UInt128
    """See [credits_posted](https://docs.tigerbeetle.com/reference/account-balances#credits_posted)"""
    timestamp: uint.UInt64
    """See [timestamp](https://docs.tigerbeetle.com/reference/account-balances#timestamp)"""


class Operation(enum.IntEnum):
    """Available operations."""

    PULSE = 128
    CREATE_ACCOUNTS = 129
    CREATE_TRANSFERS = 130
    LOOKUP_ACCOUNTS = 131
    LOOKUP_TRANSFERS = 132
    GET_ACCOUNT_TRANSFERS = 133
    GET_ACCOUNT_BALANCES = 134
