|pypi| |license| |coverage| |scru| |master_build| |docs|

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

Install latest version from PYPI

.. code:: bash

    pip install -U steam

Install the current dev version from ``github``

.. code:: bash

    pip install git+https://github.com/ValvePython/steam#egg=steam

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

IRC: irc.gamesurge.net / #opensteamworks


.. _Steam: https://store.steampowered.com/

.. |pypi| image:: https://img.shields.io/pypi/v/steam.svg?style=flat&label=stable
    :target: https://pypi.python.org/pypi/steam
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/pypi/l/steam.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/steam
    :alt: MIT License

.. |coverage| image:: https://scrutinizer-ci.com/g/ValvePython/steam/badges/coverage.png?b=master
    :target: https://scrutinizer-ci.com/g/ValvePython/steam/?branch=master
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
