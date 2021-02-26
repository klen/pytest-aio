from __future__ import annotations

import asyncio
import typing as t
from abc import ABCMeta, abstractmethod
from contextlib import contextmanager


try:
    import curio
except ImportError:
    curio = None

try:
    import trio
except ImportError:
    trio = None


class AIORunner(metaclass=ABCMeta):

    def __init__(self, **params):
        pass

    @abstractmethod
    def close(self):
        """Close the runner."""

    @abstractmethod
    def run(self, fn: t.Callable[..., t.Awaitable], *args, **kwargs):
        """Run the given coroutine function."""

    def __enter__(self) -> AIORunner:
        return self

    def __exit__(self, *args):
        self.close()


class AsyncioRunner(AIORunner):

    def __init__(self, debug: bool = False, use_uvloop: bool = True):
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

    def run(self, fn: t.Callable[..., t.Awaitable], *args, **kwargs):
        return self._loop.run_until_complete(fn(*args, **kwargs))

    def close(self):
        try:
            tasks = asyncio.all_tasks(self._loop)
            for task in tasks:
                task.cancel()

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
            raise RuntimeError('Curio is not installed.')

        self._kernel = curio.Kernel(**params)

    def close(self):
        self._kernel.run(shutdown=True)

    def run(self, fn: t.Callable[..., t.Awaitable], *args, **kwargs):

        async def helper():
            return await fn(*args, **kwargs)

        return self._kernel.run(helper)


class TrioRunner(AIORunner):

    def __init__(self, **params):
        if trio is None:
            raise RuntimeError('Trio is not installed.')
        self.params = params

    def close(self):
        pass

    def run(self, fn: t.Callable[..., t.Awaitable], *args, **kwargs):

        async def helper():
            return await fn(*args, **kwargs)

        return trio.run(helper, **self.params)


CURRENT_RUNNER = None


@contextmanager
def get_runner(aiolib: str, **params) -> t.Generator[AIORunner, t.Any, None]:
    global CURRENT_RUNNER
    if CURRENT_RUNNER:
        yield CURRENT_RUNNER
        return

    Runner: t.Type[AIORunner] = AsyncioRunner

    if aiolib.startswith('trio'):
        Runner = TrioRunner

    elif aiolib.startswith('curio'):
        Runner = CurioRunner

    try:
        with Runner(**params) as runner:
            CURRENT_RUNNER = runner
            yield runner

    finally:
        CURRENT_RUNNER = None
