import pytest
from contextvars import ContextVar


test_var: ContextVar = ContextVar('test_var')


#  @pytest.fixture
#  def aiolib():
#      return ('asyncio', {'use_uvloop': False})

#  @pytest.fixture
#  def aiolib():
#      #  return ('asyncio', {'use_uvloop': False})
#      #  return 'trio'
#      return 'curio'


@pytest.fixture
async def fixture():
    token = test_var.set(42)
    return token


async def test_contextvars(fixture):
    assert fixture
    assert test_var.get(404) == 42
    test_var.reset(fixture)
    assert test_var.get(404) == 404


async def test_contextvars2():
    assert test_var.get(404) == 404
