import asyncio

import pytest


@pytest.fixture
def aiolib():
    return "asyncio"


async def test_running_loop():
    loop = asyncio.events.get_running_loop()
    assert loop is not None


async def test_current_task():
    assert asyncio.current_task()
    assert asyncio.tasks.current_task()


async def test_create_task():
    async def coro():
        await asyncio.sleep(0.01)
        return "done"

    task = asyncio.create_task(coro())
    result = await task
    assert result == "done"
