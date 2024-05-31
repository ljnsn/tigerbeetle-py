"""PDM build hooks."""


def pdm_build_update_setup_kwargs(context, setup_kwargs):
    setup_kwargs.update(cffi_modules=["build.py:ffibuilder"])
