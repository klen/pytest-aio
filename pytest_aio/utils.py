import asyncio
from typing import Tuple, TypeVar

from asyncio.tasks import _task_name_counter  # type: ignore

try:
    import trio
except ImportError:
    trio = None  # type: ignore[assignment]

try:
    import curio  # type: ignore[import-untyped]
except ImportError:
    curio = None  # type: ignore[assignment]


TvObj = TypeVar("TvObj")


def get_testfunc(obj: TvObj) -> Tuple[TvObj, bool]:
    if hasattr(obj, "hypothesis"):
        return obj.hypothesis.inner_test, True
    return obj, False


class AsyncioContextTask(asyncio.tasks._PyTask):  # type: ignore
    def __init__(self, coro, context, loop):
        asyncio.futures._PyFuture.__init__(self, loop=loop)

        if self._source_traceback:
            del self._source_traceback[-1]

        self._name = f"Task-pytest-aio-{_task_name_counter()}"

        self._must_cancel = False
        self._fut_waiter = None
        self._coro = coro
        self._context = context
        self._num_cancels_requested = 0

        self._loop.call_soon(self._Task__step, context=self._context)
        asyncio._register_task(self)
