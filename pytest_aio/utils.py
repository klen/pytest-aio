import asyncio

try:
    from asyncio.tasks import _task_name_counter  # type: ignore
except ImportError:  # support py37
    import itertools

    _task_name_counter = itertools.count(1).__next__

try:
    import trio
except ImportError:
    trio = None

try:
    import curio
except ImportError:
    curio = None


def get_testfunc(obj):
    if hasattr(obj, 'hypothesis'):
        return obj.hypothesis.inner_test, True
    return obj, False


class AsyncioContextTask(asyncio.tasks._PyTask):  # type: ignore

    def __init__(self, coro, context, loop):
        asyncio.futures._PyFuture.__init__(self, loop=loop)

        if self._source_traceback:
            del self._source_traceback[-1]

        self._name = f'Task-pytest-aio-{_task_name_counter()}'

        self._must_cancel = False
        self._fut_waiter = None
        self._coro = coro
        self._context = context

        self._loop.call_soon(self._Task__step, context=self._context)
        asyncio._register_task(self)
