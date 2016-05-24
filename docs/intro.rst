.. include:: global.rst

Intro - steam |version|
=======================

|today|

|license|

A python module for interacting with various parts of Steam_.

Supports Python ``2.7+`` and ``3.4+``.

Main features
=============

* :doc:`SteamID <api/steam.steamid>` - convert between the various ID representations with ease
* :doc:`WebAPI <api/steam.webapi>` - simple API for Steam's Web API with automatic population of interfaces
* :doc:`WebAuth <api/steam.webauth>` - authentication for access to ``store.steampowered.com`` and ``steamcommunity.com``
* :doc:`SteamClient <api/steam.client>` - communication with the steam network based on ``gevent``.

Checkout the :doc:`user_guide` for examples, or the :doc:`api/index` for details.

For questions, issues, or general curiosity, visit the repo at `https://github.com/ValvePython/steam <https://github.com/ValvePython/steam>`_.

Installation
============

By default the ``steam`` package doesn't install all dependencies.
Add ``[client]`` extra if you are going to use :class:`SteamClient <steam.client.SteamClient>`.

Install latest version from PYPI::

    pip install -U steam
    pip install -U steam[client]

Install the current dev version from ``github``::

    pip install git+https://github.com/ValvePython/steam
    pip install git+https://github.com/ValvePython/steam#egg=steam[client]

For extras syntax in ``requirements.txt`` see `pip docs <https://pip.pypa.io/en/stable/reference/pip_install/#requirement-specifiers>`_
