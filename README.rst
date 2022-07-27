| |pypi| |latest| |pypipy| |license|
| |coverage| |master_build| |docs|
| |sonar_maintainability| |sonar_reliability| |sonar_security|

A python module for interacting with various parts of Steam_.

Supports Python ``2.7+`` and ``3.4+``.

Documentation: http://steam.readthedocs.io/en/latest/

Features
--------

* `SteamClient <http://steam.readthedocs.io/en/latest/api/steam.client.html>`_ - communication with the steam network based on ``gevent``.
* `CDNClient <http://steam.readthedocs.io/en/latest/api/steam.client.cdn.html>`_ - access to Steam content depots
* `WebAuth <http://steam.readthedocs.io/en/latest/api/steam.webauth.html>`_ - authentication for access to ``store.steampowered.com`` and ``steamcommunity.com``
* `WebAPI <http://steam.readthedocs.io/en/latest/api/steam.webapi.html>`_ - simple API for Steam's Web API with automatic population of interfaces
* `SteamAuthenticator <http://steam.readthedocs.io/en/latest/api/steam.guard.html>`_ - enable/disable/manage two factor authentication for Steam accounts
* `SteamID <http://steam.readthedocs.io/en/latest/api/steam.steamid.html>`_  - convert between the various ID representations with ease
* `Master Server Query Protocol <https://steam.readthedocs.io/en/latest/api/steam.game_servers.html>`_ - query masters servers directly or via ``SteamClient``

Checkout the `User guide <http://steam.readthedocs.io/en/latest/user_guide.html>`_ for examples,
or the `API Reference <http://steam.readthedocs.io/en/latest/api/steam.html>`_ for details.

For questions, issues or general curiosity visit the repo at `https://github.com/ValvePython/steam <https://github.com/ValvePython/steam>`_.

Like using the command line? Try `steamctl <https://github.com/ValvePython/steamctl>`_ tool

Install
-------

For system specific details, see `Installation Details <http://steam.readthedocs.io/en/latest/install.html>`_.

Install latest release version from PYPI:

.. code:: bash

    # with SteamClient dependecies
    pip install -U "steam[client]"

    # without (only when using parts that do no rely on gevent, and protobufs)
    pip install -U steam

Installing directly from ``github`` repository:

.. code:: bash

    # cutting edge from master
    pip install "git+https://github.com/ValvePython/steam#egg=steam"

    # specific version tag (e.g. v1.0.0)
    pip install "git+https://github.com/ValvePython/steam@v1.0.0#egg=steam[client]"
    # without SteamClient extras
    pip install "git+https://github.com/ValvePython/steam@v1.0.0#egg=steam"

Vagrant
-------

The repo includes a `Vagrantfile` to setup enviroment for expermentation and development.
We assume you've already have ``vagrant`` and ``virtualbox`` set up.
The VM is ``Ubuntu 16.04`` with all necessary packages installed, and virtualenv for ``python2`` and ``python3``.


.. code:: bash

    vagrant up    # spin the VM and let it setup
    vagrant ssh
    # for python2
    $ source venv2/bin/activate
    # for python3
    $ source venv3/bin/activate



Local Testing
-------------

To run the test suite with the current ``python``, use

.. code:: bash

    make test

To run for specific version, setup a virtual environment

.. code:: bash

    virtualenv -p python3 py3
    source py3/bin/active
    pip install -r requirements.txt
    make test

Contact
-------

IRC: irc.libera.chat / #steamre (`join via webchat <https://web.libera.chat/#steamre>`_)


.. _Steam: https://store.steampowered.com/

.. |pypi| image:: https://img.shields.io/pypi/v/steam.svg?label=pypi&color=green
    :target: https://pypi.python.org/pypi/steam
    :alt: Latest version released on PyPi

.. |latest| image:: https://img.shields.io/github/v/tag/ValvePython/steam?include_prereleases&sort=semver&label=release
   :target: https://github.com/ValvePython/steam/releases
   :alt: Latest release on Github

.. |pypipy| image:: https://img.shields.io/pypi/pyversions/steam.svg?label=%20&logo=python&logoColor=white
    :alt: PyPI - Python Version

.. |license| image:: https://img.shields.io/pypi/l/steam.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/steam
    :alt: MIT License

.. |coverage| image:: https://img.shields.io/coveralls/ValvePython/steam/master.svg?style=flat
    :target: https://coveralls.io/r/ValvePython/steam?branch=master
    :alt: Test coverage

.. |sonar_maintainability| image:: https://sonarcloud.io/api/project_badges/measure?project=ValvePython_steam&metric=sqale_rating
    :target: https://sonarcloud.io/dashboard?id=ValvePython_steam
    :alt: SonarCloud Rating

.. |sonar_reliability| image:: https://sonarcloud.io/api/project_badges/measure?project=ValvePython_steam&metric=reliability_rating
    :target: https://sonarcloud.io/dashboard?id=ValvePython_steam
    :alt: SonarCloud Rating

.. |sonar_security| image:: https://sonarcloud.io/api/project_badges/measure?project=ValvePython_steam&metric=security_rating
    :target: https://sonarcloud.io/dashboard?id=ValvePython_steam
    :alt: SonarCloud Rating

.. |master_build| image:: https://img.shields.io/travis/ValvePython/steam/master.svg?style=flat&label=master
    :target: http://travis-ci.org/ValvePython/steam/branches
    :alt: Build status of master branch

.. |docs| image:: https://readthedocs.org/projects/steam/badge/?version=latest
    :target: http://steam.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation status
