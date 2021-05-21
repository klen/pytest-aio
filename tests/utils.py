import asyncio

import sniffio


def aio_sleep(seconds):
    from pytest_aio.runners import trio, curio

    if sniffio.current_async_library() == 'trio':
        return trio.sleep(seconds)

    if sniffio.current_async_library() == 'curio':
        return curio.sleep(seconds)

    return asyncio.sleep(seconds)
