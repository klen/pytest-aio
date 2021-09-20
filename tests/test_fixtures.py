import pytest
import sniffio


@pytest.fixture(scope='module')
def events():
    return []


@pytest.fixture
def sync_fixture():
    return 'sync_fixture'


@pytest.fixture
def sync_gen_fixture():
    yield 'sync_gen_fixture'


@pytest.fixture
async def async_fixture(pytestconfig, aiolib, aiosleep):
    await aiosleep(1e-2)
    return 'async_fixture'


@pytest.fixture
async def async_gen_fixture(events, request, aiosleep):
    events.append((id(request), 'start'))
    await aiosleep(1e-2)
    yield 'async_gen_fixture'
    events.append((id(request), 'finish'))


def test_sync_fixtures(sync_fixture, sync_gen_fixture):
    assert sync_fixture == 'sync_fixture'
    assert sync_gen_fixture == 'sync_gen_fixture'


async def test_async_fixtures(async_fixture, async_gen_fixture, aiosleep):
    await aiosleep(1e-2)
    assert async_fixture == 'async_fixture'
    assert async_gen_fixture == 'async_gen_fixture'


def test_sync_with_async_fixtures(async_fixture):
    assert async_fixture == 'async_fixture'


def test_sync_with_async_fixtures2(async_gen_fixture, aiolib):
    assert async_gen_fixture == 'async_gen_fixture'


def test_events(events):
    for (e1, e2) in zip(events[::2], events[1::2]):
        assert e1[0] == e2[0]
        assert e1[1] == 'start'
        assert e2[1] == 'finish'


async def test_aiosleep(aiosleep):
    await aiosleep(1e-2)
    assert True
