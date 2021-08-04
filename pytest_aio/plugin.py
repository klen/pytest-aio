import typing as t
from inspect import iscoroutinefunction, isasyncgenfunction

import pytest

from .runners import get_runner
from .utils import get_testfunc, trio, curio


DEFAULT_AIOLIBS = ['asyncio', *(trio and ['trio'] or []), *(curio and ['curio'] or [])]


@pytest.fixture(params=DEFAULT_AIOLIBS, scope='session')
def aiolib(request):
    return request.param


@pytest.hookimpl(tryfirst=True)
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.istestfunction(obj, name):
        testfunc, _ = get_testfunc(obj)
        if iscoroutinefunction(testfunc):
            pytest.mark.usefixtures('aiolib')(obj)


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> t.Optional[bool]:
    backend = pyfuncitem.funcargs.get('aiolib')
    if not backend:
        return

    aiolib, params = backend
    testfunc, is_hypothesis = get_testfunc(pyfuncitem.obj)
    if not iscoroutinefunction(testfunc):
        return

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
    if fixturedef.argname == 'aiolib':

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
    if 'aiolib' not in fixturedef.argnames:
        fixturedef.argnames += 'aiolib',

    def wrapper(*args, aiolib, **kwargs):
        lib, params = aiolib
        if 'aiolib' in argnames:
            kwargs['aiolib'] = aiolib

        with get_runner(lib, **params) as runner:
            if iscoroutinefunction(func):
                yield runner.run(func, *args, **kwargs)
                return

            gen = func(*args, **kwargs)
            while True:
                try:
                    yield runner.run(gen.asend, None)
                except (StopIteration, StopAsyncIteration):
                    break

                #  try:
                #      yield runner.run(gen.asend, None)
                #  except StopIteration:
                #      raise RuntimeError(f"Fixture `{func}` did not yield")

                #  runner.run(gen.asend, None)
                #  try:
                #      runner.run(gen.asend, None)
                #  except StopAsyncIteration:
                #      pass
                #  else:
                #      runner.run(gen.aclose)
                #      raise RuntimeError('Async generator fixture did not stop')

    fixturedef.func = wrapper
