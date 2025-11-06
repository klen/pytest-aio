import pytest
from contextvars import ContextVar

test_var: ContextVar = ContextVar("test_var")


@pytest.fixture
async def fixture():
    token = test_var.set(42)
    return token


@pytest.fixture
async def async_gen_fixture():
    token = test_var.set(42)
    yield
    test_var.reset(token)


async def test_contextvars(fixture):
    assert fixture
    assert test_var.get(404) == 42
    test_var.reset(fixture)
    assert test_var.get(404) == 404


async def test_contextvars2():
    assert test_var.get(404) == 404


async def test_contextvars3(async_gen_fixture):
    assert True
