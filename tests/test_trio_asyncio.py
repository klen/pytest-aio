import pytest
import sys

if sys.version_info >= (3, 14):
    pytest.skip("Trio-Asyncio tests are not supported on Python 3.14+", allow_module_level=True)


@pytest.fixture
def aiolib():
    return ("trio", {"trio_asyncio": True})


async def test_base():
    import trio

    await trio.sleep(1e-2)


async def test_trio_asyncio():
    import asyncio
    import trio_asyncio  # type: ignore[import-untyped]

    await trio_asyncio.aio_as_trio(asyncio.sleep)(1e-2)
    assert True
