.. include:: global.rst

Intro - steam |version|
=======================

|today|

|license|

A python module for interacting with various parts of Steam_.

Supports Python ``2.7+`` and ``3.4+``.

Features
========

* :doc:`SteamClient <api/steam.client>` - communication with the steam network based on ``gevent``
* :doc:`CDNClient <api/steam.client.cdn>` - access to Steam content depots
* :doc:`WebAuth <api/steam.webauth>` - authentication for access to ``store.steampowered.com`` and ``steamcommunity.com``
* :doc:`WebAPI <api/steam.webapi>` - simple API for Steam's Web API with automatic population of interfaces
* :doc:`SteamAuthenticator <api/steam.guard>` - enable/disable/manage two factor authentication for Steam accounts
* :doc:`SteamID <api/steam.steamid>` - convert between the various ID representations with ease
* :doc:`Master Server Query Protocol <api/steam.game_servers>` - query masters servers directly or via ``SteamClient``

Checkout the :doc:`user_guide` for examples, or the :doc:`api/steam` for details.

For questions, issues, or general curiosity, visit the repo at `https://github.com/ValvePython/steam <https://github.com/ValvePython/steam>`_.

Like using the command line? Try `steamctl <https://github.com/ValvePython/steamctl>`_ tool

Quick install
=============

For system specific details, see :doc:`install`.

Install latest version from PYPI::

    # with SteamClient dependecies
    pip install -U steam[client]

    # without (only when using parts that do no rely on gevent, and protobufs)
    pip install -U steam

Install the current dev version from ``github``::

    # cutting edge from master
    pip install git+https://github.com/ValvePython/steam#egg=steam

    # specific version tag (e.g. v1.0.0)
    pip install git+https://github.com/ValvePython/steam@v1.0.0#egg=steam[client]
    # without SteamClient extras
    pip install git+https://github.com/ValvePython/steam@v1.0.0#egg=steam
