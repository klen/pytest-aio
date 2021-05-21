import pytest


@pytest.fixture(params=['trio', 'curio'])
def aiolib(request):
    return request.param


def test_custom_aiolib(aiolib):
    assert isinstance(aiolib, tuple)
    libname, params = aiolib
    assert libname in {'trio', 'curio'}
