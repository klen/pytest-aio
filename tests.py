import asyncio

import pytest
import sniffio

from hypothesis import given, strategies


# Fixtures
# --------

@pytest.fixture
def sync_fixture():
    return 'sync_fixture'


@pytest.fixture
def sync_gen_fixture():
    yield 'sync_gen_fixture'


@pytest.fixture
async def async_fixture():
    await aio_sleep(1e-2)
    return 'async_fixture'


@pytest.fixture
async def async_gen_fixture():
    await aio_sleep(1e-2)
    yield 'async_gen_fixture'


# Tests
# -----

def test_sync(sync_fixture, sync_gen_fixture):
    assert sync_fixture == 'sync_fixture'
    assert sync_gen_fixture == 'sync_gen_fixture'


async def test_async(aiolib):
    await aio_sleep(1e-2)
    assert sniffio.current_async_library() == aiolib


async def test_async_fixture(async_fixture):
    await aio_sleep(1e-2)
    assert async_fixture == 'async_fixture'


async def test_async_gen_fixture(async_gen_fixture):
    await aio_sleep(1e-2)
    assert async_gen_fixture == 'async_gen_fixture'


@pytest.mark.parametrize('aiolib', ['trio', 'curio'])
async def test_custom_aiolibs():
    assert sniffio.current_async_library() in {'trio', 'curio'}


@given(strategies.integers())
async def test_hypothesis(n):
    assert isinstance(n, int)


@pytest.mark.parametrize("y", [1, 2])
@given(x=strategies.none())
async def test_mark_and_parametrize(x, y):
    assert x is None
    assert y in (1, 2)


# Utils
# -----

def aio_sleep(seconds):
    from pytest_aio.runners import trio, curio

    if sniffio.current_async_library() == 'trio':
        return trio.sleep(seconds)

    if sniffio.current_async_library() == 'curio':
        return curio.sleep(seconds)

    return asyncio.sleep(seconds)
