import pytest

from .utils import aio_sleep


@pytest.fixture
def sync_fixture():
    return 'sync_fixture'


@pytest.fixture
def sync_gen_fixture():
    yield 'sync_gen_fixture'


@pytest.fixture
async def async_fixture(aiolib):
    await aio_sleep(1e-2)
    return 'async_fixture'


@pytest.fixture
async def async_gen_fixture():
    await aio_sleep(1e-2)
    yield 'async_gen_fixture'


def test_sync_fixtures(sync_fixture, sync_gen_fixture):
    assert sync_fixture == 'sync_fixture'
    assert sync_gen_fixture == 'sync_gen_fixture'


async def test_async_fixtures(async_fixture, async_gen_fixture):
    await aio_sleep(1e-2)
    assert async_fixture == 'async_fixture'
    assert async_gen_fixture == 'async_gen_fixture'


def test_sync_with_async_fixtures(async_fixture):
    assert async_fixture == 'async_fixture'
