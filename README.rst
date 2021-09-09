pytest-aio
==========

.. _description:

**pytest-aio** -- Is a simple pytest_ plugin for testing any async python code

.. _badges:

.. image:: https://github.com/klen/pytest-aio/workflows/tests/badge.svg
    :target: https://github.com/klen/pytest-aio/actions
    :alt: Tests Status

.. image:: https://img.shields.io/pypi/v/pytest-aio
    :target: https://pypi.org/project/pytest-aio/
    :alt: PYPI Version

.. image:: https://img.shields.io/pypi/pyversions/pytest-aio
    :target: https://pypi.org/project/pytest-aio/
    :alt: Python Versions

Features
--------

- Supports all most popular async python libraries: `Asyncio`_, `Trio`_ and Curio_
- Automatically run your async tests
- Works with `contextvars` correctly (supports it for async/sync fixtures)
- Supports `trio-asyncio`_

.. _contents:

.. contents::

.. _requirements:

Requirements
=============

- python >= 3.7

Installation
=============

**pytest-aio** should be installed using pip: ::

    pip install pytest-aio

optionally extras are available: ::

    pip install pytest-aio[curio,trio]

Usage
=====

When installed the plugin runs all your async test functions/fixtures.

.. code-block:: python

    async def test_async():
        assert True

No need to mark your async tests. Just run pytest as is.

Async fixtures for sync tests
-----------------------------

If you plan use async fixtures for sync tests, please ensure you have to
include `aiolib` fixture:

.. code-block:: python

    # It's important to add aiolib fixture here
    def test_with_async_fixtures(async_fixture, aiolib):
        assert async_fixture == 'value from async fixture'

As an alternative, If you are doing the async fixtures yourself, you can add
`aiolib` inside them:

.. code-block:: python

    @pytest.fixture
    async def async_fixture(aiolib):
        return 'value from async fixture'

    # So for the test we don't need to implicity use `aiolib` anymore
    def test_with_async_fixtures(async_fixture):
        assert async_fixture == 'value from async fixture'


Customize async libraries
-------------------------

By default each test function will be run with asyncio, trio, curio backends
consistently (only if trio/curio are installed). But you can customise the
libraries for all your tests creating the global fixture:

.. code-block:: python

    # Run all tests with Asyncio/Trio only
    @pytest.fixture(params=['asyncio', 'trio'])
    def aiolib(request):
        assert request.param

If you want to specify different options for the selected backend, you can do
so by passing a tuple of (backend name, options dict):

.. code-block:: python

    @pytest.fixture(params=[
        pytest.param(('asyncio', {'use_uvloop': False}), id='asyncio'),
        pytest.param(('asyncio', {'use_uvloop': True}), id='asyncio+uvloop'),
        pytest.param(('trio', {'trio_asyncio': True}), id='trio+asyncio'),
        pytest.param(('curio', {'debug': True}), id='curio'),
    ])
    def aiolib(request):
        assert request.param

To set a specific backends for a single test only:

.. code-block:: python

    @pytest.mark.parametrize('aiolib', ['asyncio'])
    async def only_with_asyncio():
        await asyncio.sleep(1)
        assert True


.. _bugtracker:

Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/asgi-tools/issues

.. _contributing:

Contributing
============

Development of the project happens at: https://github.com/klen/pytest-aio

.. _license:

License
========

Licensed under a `MIT license`_.


.. _links:

.. _Asyncio: https://docs.python.org/3/library/asyncio.html
.. _Curio: https://curio.readthedocs.io/en/latest/
.. _MIT license: http://opensource.org/licenses/MIT
.. _Trio: https://trio.readthedocs.io/en/stable/index.html
.. _klen: https://github.com/klen
.. _pytest: https://docs.pytest.org/en/stable/
.. _AnyIO: https://github.com/agronholm/anyio
.. _trio-asyncio: https://github.com/python-trio/trio-asyncio 
