from __future__ import annotations

import asyncio
from contextvars import Context
from inspect import isasyncgenfunction, iscoroutinefunction
from typing import Dict, Optional, Tuple

import pytest

from .runners import get_runner
from .utils import curio, get_testfunc, trio

DEFAULT_AIOLIBS = ["asyncio", *(trio and ["trio"] or []), *(curio and ["curio"] or [])]


@pytest.fixture(params=DEFAULT_AIOLIBS, scope="session")
def aiolib(request):
    """Iterate async libraries."""
    return request.param


@pytest.fixture()
def aiocontext(aiolib, request):
    """Update context."""
    return Context()


@pytest.fixture()
def aiosleep(aiolib):
    name = aiolib[0]
    if name == "asyncio":
        return asyncio.sleep

    if name == "trio":
        return trio.sleep

    if name == "curio":
        return curio.sleep
    return None


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """Mark async functions."""
    if collector.istestfunction(obj, name):
        testfunc, _ = get_testfunc(obj)
        if iscoroutinefunction(testfunc):
            pytest.mark.usefixtures("aiolib")(obj)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> Optional[bool]:
    backend: Tuple[str, Dict] = pyfuncitem.funcargs.get("aiolib")  # type: ignore[assignment]
    if not backend:
        return None

    aiolib, params = backend
    testfunc, is_hypothesis = get_testfunc(pyfuncitem.obj)
    if not iscoroutinefunction(testfunc):
        return None

    def run(**kwargs):
        with get_runner(aiolib, **params) as runner:
            runner.run(testfunc, **kwargs)

    if is_hypothesis:
        pyfuncitem.obj.hypothesis.inner_test = run

    else:
        funcargs = pyfuncitem.funcargs
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        run(**testargs)

    return True


def pytest_fixture_setup(fixturedef, request):
    """Support async fixtures."""

    func = fixturedef.func

    # Fix aiolib fixture
    if fixturedef.argname == "aiolib":

        def fix_aiolib(*args, **kwargs):
            """Convert aiolib fixture value to a tuple."""
            aiolib = func(*args, **kwargs)
            return aiolib if isinstance(aiolib, tuple) else (aiolib, {})

        fixturedef.func = fix_aiolib
        return

    # Skip sync functions
    if not (iscoroutinefunction(func) or isasyncgenfunction(func)):
        return

    argnames = fixturedef.argnames
    if "aiolib" not in fixturedef.argnames:
        fixturedef.argnames += ("aiolib",)

    def wrapper(*args, aiolib, **kwargs):
        lib, params = aiolib
        if "aiolib" in argnames:
            kwargs["aiolib"] = aiolib

        with get_runner(lib, **params) as runner:
            if iscoroutinefunction(func):
                yield runner.run(func, *args, **kwargs)
                return

            gen = func(*args, **kwargs)
            try:
                yield runner.run(gen.__anext__().__await__)
            except StopAsyncIteration:
                raise RuntimeError("Async generator did not yield") from None

            try:
                runner.run(gen.__anext__().__await__)
            except StopAsyncIteration:
                pass
            else:
                runner.run(gen.aclose)
                raise RuntimeError("Async generator fixture did not stop")

    fixturedef.func = wrapper
