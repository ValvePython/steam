|pypi| |license| |coverage| |scru| |master_build| |docs|

A python module for interacting with various parts of Steam_.

Supports Python ``2.7+`` and ``3.3+``.

Documentation: http://steam.readthedocs.io/en/latest/

Key features
------------

* `SteamAuthenticator <http://steam.readthedocs.io/en/latest/api/steam.guard.html>`_ - enable/disable/manage 2FA on account and generate codes
* `SteamClient <http://steam.readthedocs.io/en/latest/api/steam.client.html>`_ - communication with the steam network based on ``gevent``.
* `SteamID <http://steam.readthedocs.io/en/latest/api/steam.client.html>`_  - convert between the various ID representations with ease
* `WebAPI <http://steam.readthedocs.io/en/latest/api/steam.webapi.html>`_ - simple API for Steam's Web API with automatic population of interfaces
* `WebAuth <http://steam.readthedocs.io/en/latest/api/steam.webauth.html>`_ - authentication for access to ``store.steampowered.com`` and ``steamcommunity.com``

Checkout the `User guide <http://steam.readthedocs.io/en/latest/steam/user_guide.html>`_ for examples,
or the `API Reference <http://steam.readthedocs.io/en/latest/steam/api/index.html>`_ for details.

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
    pip install -r requirements.txt
    make test

To run for ``python 2.7`` and ``3.4`` assuming you have them installed::

    tox


.. _Steam: https://store.steampowered.com/

.. |pypi| image:: https://img.shields.io/pypi/v/steam.svg?style=flat&label=stable
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
    :target: http://travis-ci.org/ValvePython/steam/branches
    :alt: Build status of master branch

.. |docs| image:: https://readthedocs.org/projects/steam/badge/?version=latest
    :target: http://steam.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation status
