import typing as t
from inspect import iscoroutinefunction, isasyncgenfunction

import pytest

from .runners import get_runner
from .utils import get_testfunc, trio, curio


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
        return None

    testfunc, is_hypothesis = get_testfunc(pyfuncitem.obj)
    if not iscoroutinefunction(testfunc):
        return None

    aiolib, params = pyfuncitem.funcargs.get('aiolib', 'asyncio')

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
    func = fixturedef.func
    if fixturedef.argname == 'aiolib':

        def wrapper(*args, **kwargs):
            aiolib = func(*args, **kwargs)
            return aiolib if isinstance(aiolib, tuple) else (aiolib, {})

        fixturedef.func = wrapper
        return

    if not (iscoroutinefunction(func) or isasyncgenfunction(func)):
        return

    def wrapper(*args, aiolib, **kwargs):
        lib, params = aiolib
        with get_runner(lib, **params) as runner:
            if iscoroutinefunction(func):
                yield runner.run(func, *args, **kwargs)

            else:
                gen = func(*args, **kwargs)
                try:
                    value = runner.run(gen.asend, None)
                except StopIteration:
                    raise RuntimeError('Async generator did not yield')

                yield value

                try:
                    runner.run(gen.asend, None)
                except StopAsyncIteration:
                    pass
                else:
                    runner.run(gen.aclose)
                    raise RuntimeError('Async generator fixture did not stop')

    fixturedef.func = wrapper
    if 'aiolib' not in fixturedef.argnames:
        fixturedef.argnames += 'aiolib',


DEFAULT_AIOLIBS = ['asyncio', *(trio and ['trio'] or []), *(curio and ['curio'] or [])]


@pytest.fixture(params=DEFAULT_AIOLIBS, scope='session')
def aiolib(request):
    return request.param
