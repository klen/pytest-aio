"""Setup async envs."""

import pytest
import uvloop


@pytest.fixture(
    params=[
        pytest.param("asyncio", id="asyncio"),
        pytest.param(("asyncio", {"loop_factory": uvloop.new_event_loop}), id="asyncio+uvloop"),
        pytest.param(("trio", {"restrict_keyboard_interrupt_to_checkpoints": True}), id="trio"),
        "curio",
    ]
)
def aiolib(request):
    return request.param
