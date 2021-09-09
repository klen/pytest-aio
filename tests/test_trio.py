import pytest


@pytest.fixture(params=[
    pytest.param(('trio', {}), id='trio'),
    pytest.param(
        ('trio', {'restrict_keyboard_interrupt_to_checkpoints': True}), id='trio-keyboard'),
    pytest.param(('trio', {'trio_asyncio': True}), id='trio-asyncio'),
])
def aiolib(request):
    return request.param


async def test_base():
    import trio

    await trio.sleep(1e-2)
    assert True


@pytest.mark.parametrize('aiolib', [('trio', {'trio_asyncio': True})])
async def test_trio_asyncio():
    import asyncio
    import trio_asyncio

    await trio_asyncio.aio_as_trio(asyncio.sleep)(1e-2)
    assert True
