"""Generates the CFFI bindings for the tb_client library."""

import platform
from pathlib import Path

import cffi


def get_sys_info():
    """Get the target architecture of the current system."""
    arch = platform.machine()
    system = platform.system().lower()
    if system != "linux":
        return f"{arch}-{system}"
    libc = "gnu" if platform.libc_ver()[0] == "glibc" else "musl"
    return f"{arch}-{system}-{libc}"


this_dir = Path().parent.absolute()
lib_dir = this_dir.joinpath("lib", get_sys_info())
h_file = this_dir.joinpath("src", "tigerbeetle_py", "_native", "tb_client.h")

ffibuilder = cffi.FFI()

with h_file.open() as c_header:
    c_header = c_header.read()

defs = f"""\
{c_header}

extern "Python" void on_completion_fn(uintptr_t, tb_client_t, tb_packet_t*, const uint8_t*, uint32_t);
"""

ffibuilder.cdef(defs)

ffibuilder.set_source(
    "tigerbeetle_py._native.tb_client",
    c_header,
    libraries=["tb_client"],
    library_dirs=[lib_dir.as_posix()],
    extra_link_args=[f"-Wl,-rpath,{lib_dir.as_posix()}"],
)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
