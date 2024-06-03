"""Integration tests configuration."""

import subprocess
from collections.abc import Iterable
from pathlib import Path

import pytest
from tigerbeetle_py import Client, uint


@pytest.fixture(scope="session")
def port() -> int:
    """Return the default port."""
    return 3033


@pytest.fixture(scope="session")
def cluster_id() -> uint.UInt128:
    """Return the default cluster ID."""
    return uint.UInt128(0)


@pytest.fixture(scope="session")
def replica_id() -> int:
    """Return the default replica ID."""
    return 0


@pytest.fixture(scope="session")
def replica_count() -> int:
    """Return the default replica count."""
    return 1


@pytest.fixture(scope="session")
def concurrency_max() -> int:
    """Return the maximum concurrency."""
    return 8192


@pytest.fixture(scope="session")
def tigerbeetle_cmd() -> str:
    """Return the default TigerBeetle command."""
    return "tigerbeetle"


@pytest.fixture(scope="session")
def db_file(
    tigerbeetle_cmd: str,
    cluster_id: uint.UInt128,
    replica_id: int,
    replica_count: int,
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterable[Path]:
    """Return the default database file."""
    cluster_id_arg = f"--cluster={cluster_id}"
    replica_arg = f"--replica={replica_id}"
    replica_count_arg = f"--replica-count={replica_count}"
    file_name = f"{cluster_id}_{replica_id}.tigerbeetle"
    file_path = tmp_path_factory.mktemp("db") / file_name

    cmd = [
        tigerbeetle_cmd,
        "format",
        cluster_id_arg,
        replica_arg,
        replica_count_arg,
        file_path.as_posix(),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    yield file_path

    # NOTE: probably not necessary since this is a temp dir
    file_path.unlink()


@pytest.fixture(scope="session")
def _tigerbeetle(
    tigerbeetle_cmd: str,
    db_file: Path,
    port: int,
    cluster_id: uint.UInt128,
) -> Iterable[None]:
    """Return the default TigerBeetle command."""
    address_arg = f"--address={port}"
    cache_size_arg = "--cache-grid=256MiB"
    cmd = [tigerbeetle_cmd, "start", address_arg, cache_size_arg, db_file.as_posix()]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("TigerBeetle started")
    yield
    print("TigerBeetle stopping")
    proc.terminate()
    # this removes the zombie process
    proc.poll()


# @pytest.fixture(scope="session")
# def tb_client(
#     _tigerbeetle: None,
#     port: int,
#     cluster_id: uint.UInt128,
#     concurrency_max: int,
# ) -> Iterable[Client]:
#     """Return the default TigerBeetle client."""
#     client = Client(cluster_id, [str(port)], concurrency_max)
#     yield client
#     client.close()


@pytest.fixture(scope="session")
def tb_client(
    cluster_id: uint.UInt128,
    port: int,
    concurrency_max: int,
) -> Iterable[Client]:
    """Return the default TigerBeetle client."""
    client = Client(cluster_id, [str(port)], concurrency_max)
    yield client
    client.close()
