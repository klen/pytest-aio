import pytest
from hypothesis import given, strategies


@given(strategies.integers())
async def test_hypothesis(n):
    assert isinstance(n, int)


@pytest.mark.parametrize("y", [1, 2])
@given(x=strategies.none())
async def test_mark_and_parametrize(x, y):
    assert x is None
    assert y in (1, 2)
