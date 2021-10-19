import pytest


@pytest.mark.parametrize('aiolib', ['asyncio', 'trio'])
async def test_lock():
    import anyio

    async with anyio.Lock():
        await anyio.sleep(1e-2)
