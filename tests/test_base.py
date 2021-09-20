import pytest

from sniffio import current_async_library


def test_sync():
    assert True


async def test_async(aiosleep):
    await aiosleep(1e-2)
    assert True


async def test_aiolib(aiolib, aiosleep):
    lib, _ = aiolib
    curlib = current_async_library()
    assert lib.startswith(curlib)


@pytest.mark.parametrize('aiolib', ['trio', 'curio'])
async def test_parametrize_aiolib(aiolib):
    assert current_async_library() in {'trio', 'curio'}
