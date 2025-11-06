import pytest


@pytest.fixture(
    params=[
        pytest.param(("trio", {}), id="trio"),
        pytest.param(
            ("trio", {"restrict_keyboard_interrupt_to_checkpoints": True}), id="trio-keyboard"
        ),
    ],
    scope="module",
)
def aiolib(request):
    return request.param


async def test_base():
    import trio

    await trio.sleep(1e-2)
