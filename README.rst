|pypi| |license| |coverage| |scru| |master_build|

A python module for interacting with various parts of Steam_.

Supports Python ``2.7+`` and ``3.4+``.

Python 3 support for the SteamClient is not available in the release, see `issue#10 <https://github.com/ValvePython/steam/issues/10>`_.

Main features:

* `SteamID <http://valvepython.github.io/steam/api/steam.client.html>`_  - convert between the various ID representations with ease
* `WebAPI <http://valvepython.github.io/steam/api/steam.webapi.html>`_ - simple API for Steam's Web API with automatic population of interfaces
* `WebAuth <http://valvepython.github.io/steam/api/steam.webauth.html>`_ - authentication for access to ``store.steampowered.com`` and ``steamcommunity.com``
* `SteamClient <http://valvepython.github.io/steam/api/steam.client.html>`_ - communication with the steam network based on ``gevent``.

Checkout the `User guide <http://valvepython.github.io/steam/user_guide.html>`_ for examples,
or the `API Reference <http://valvepython.github.io/steam/api/index.html>`_ for details.

For questions, issues or general curiosity visit the repo at `https://github.com/ValvePython/steam <https://github.com/ValvePython/steam>`_.

Installation
------------

By default the ``steam`` package doesn't install all dependecies.
Add ``[client]`` extra if you are going to use ``SteamClient``.

Install latest version from PYPI::

    pip install -U steam
    pip install -U steam[client]

Install the current dev version from ``github``::

    pip install git+https://github.com/ValvePython/steam
    pip install git+https://github.com/ValvePython/steam#egg=steam[client]

For extras syntax in ``requirements.txt`` see `pip docs <https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers>`_

Testing
-------

To run the test suite with the current ``python``, use::

    make test

To run for specific version, setup a ``virtual environment``::

    virtualenv -p python3 py3
    source py3/bin/active
    make test

To run for ``python 2.7`` and ``3.4`` assuming you have them installed::

    tox


.. _Steam: https://store.steampowered.com/

.. |pypi| image:: https://img.shields.io/pypi/v/steam.svg?style=flat&label=latest%20version
    :target: https://pypi.python.org/pypi/steam
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/pypi/l/steam.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/steam
    :alt: MIT License

.. |coverage| image:: https://img.shields.io/coveralls/ValvePython/steam/master.svg?style=flat
    :target: https://coveralls.io/r/ValvePython/steam?branch=master
    :alt: Test coverage

.. |scru| image:: https://scrutinizer-ci.com/g/ValvePython/steam/badges/quality-score.png?b=master
    :target: https://scrutinizer-ci.com/g/ValvePython/steam/?branch=master
    :alt: Scrutinizer score

.. |master_build| image:: https://img.shields.io/travis/ValvePython/steam/master.svg?style=flat&label=master
    :target: http://travis-ci.org/ValvePython/steam
    :alt: Build status of master branch
