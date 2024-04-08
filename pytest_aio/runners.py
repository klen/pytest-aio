from __future__ import annotations

import asyncio
from abc import ABCMeta, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from contextvars import copy_context
from typing import Any, Awaitable, Callable, Generator, Type

from .utils import AsyncioContextTask, curio, trio

# Patch anyio to support AsyncioContextTask
try:
    from anyio._backends import _asyncio

    _asyncio.get_coro = lambda task: task._coro  # type: ignore[attr-defined]
except ImportError:
    pass


TCoroutineFn = Callable[..., Awaitable]


class AIORunner(metaclass=ABCMeta):
    def __init__(self, **params):
        self.ctx = copy_context()

    @abstractmethod
    def close(self):
        """Close the runner."""

    @abstractmethod
    def run(self, fn: TCoroutineFn, *args, **kwargs):
        """Run the given coroutine function."""

    async def run_context_helper(self, fn: TCoroutineFn, *args, **kwargs):
        """Copy context and run the given async function."""
        ctx = self.ctx
        for var in ctx:
            var.set(ctx[var])
        try:
            return await fn(*args, **kwargs)
        finally:
            self.ctx = copy_context()

    def __enter__(self) -> AIORunner:
        return self

    def __exit__(self, *args):
        self.close()


class AsyncioRunner(AIORunner):
    def __init__(self, debug: bool = False, use_uvloop: bool = True):
        super(AsyncioRunner, self).__init__()
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
        if use_uvloop:
            try:
                import uvloop

                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            except ImportError:
                pass

        self._loop = asyncio.new_event_loop()
        self._loop.set_debug(debug)
        asyncio.set_event_loop(self._loop)

    def run(self, fn: TCoroutineFn, *args, **kwargs):
        task = AsyncioContextTask(fn(*args, **kwargs), self.ctx, self._loop)
        #  return self._loop.run_until_complete(self.run_context_helper(fn, *args, **kwargs))
        return self._loop.run_until_complete(task)

    def close(self):
        """Close remaining tasks."""
        try:
            tasks = asyncio.all_tasks(self._loop)
            if not tasks:
                return

            for task in tasks:
                task.cancel()

            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

            for task in tasks:
                if task.cancelled():
                    continue

                if task.exception() is not None:
                    raise task.exception()
        finally:
            asyncio.set_event_loop(None)
            self._loop.close()


class CurioRunner(AIORunner):
    def __init__(self, **params):
        if curio is None:
            raise RuntimeError("Curio is not installed.")

        super(CurioRunner, self).__init__()

        self._kernel = curio.Kernel(**params)

    def close(self):
        self._kernel.run(shutdown=True)

    def run(self, fn: TCoroutineFn, *args, **kwargs):
        async def helper():
            return await fn(*args, **kwargs)

        return self.ctx.run(self._kernel.run, helper)


class TrioRunner(AIORunner):
    @asynccontextmanager
    async def run_context(self):
        yield

    def __init__(self, trio_asyncio=False, **params):
        if trio is None:
            raise RuntimeError("Trio is not installed.")

        super(TrioRunner, self).__init__()
        self.params = params

        if trio_asyncio:
            import trio_asyncio as asyncio_trio  # type: ignore[import-untyped]

            self.run_context = asyncio_trio.open_loop

    def close(self):
        pass

    def run(self, fn: TCoroutineFn, *args, **kwargs):
        from sniffio import current_async_library_cvar

        async def helper():
            trio.lowlevel.current_task().context = self.ctx
            await trio.sleep(0)
            token = current_async_library_cvar.set("trio")
            async with self.run_context():
                res = await fn(*args, **kwargs)
            current_async_library_cvar.reset(token)
            return res

        return trio.run(helper, **self.params)


CURRENT_RUNNER = None


@contextmanager
def get_runner(aiolib: str, **params) -> Generator[AIORunner, Any, None]:
    global CURRENT_RUNNER
    if CURRENT_RUNNER:
        yield CURRENT_RUNNER
        return

    Runner: Type[AIORunner] = AsyncioRunner

    if aiolib.startswith("trio"):
        Runner = TrioRunner

    elif aiolib.startswith("curio"):
        Runner = CurioRunner

    try:
        with Runner(**params) as runner:
            CURRENT_RUNNER = runner
            yield runner

    finally:
        CURRENT_RUNNER = None
