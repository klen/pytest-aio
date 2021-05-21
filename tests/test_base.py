import pytest

from .utils import aio_sleep, sniffio


def test_sync():
    assert True


async def test_async():
    await aio_sleep(1e-2)
    assert True


async def test_aiolib(aiolib):
    await aio_sleep(1e-2)
    lib, _ = aiolib
    curlib = sniffio.current_async_library()
    assert lib.startswith(curlib)


@pytest.mark.parametrize('aiolib', ['trio', 'curio'])
async def test_custom_aiolibs():
    assert sniffio.current_async_library() in {'trio', 'curio'}
