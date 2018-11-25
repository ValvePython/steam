.. include:: global.rst

Intro - steam |version|
=======================

|today|

|license|

A python module for interacting with various parts of Steam_.

Supports Python ``2.7+`` and ``3.4+``.

Key features
============

* :doc:`SteamAuthenticator <api/steam.guard>` - enable/disable/manage 2FA on account and generate codes
* :doc:`SteamClient <api/steam.client>` - communication with the steam network based on ``gevent``
* :doc:`SteamID <api/steam.steamid>` - convert between the various ID representations with ease
* :doc:`WebAPI <api/steam.webapi>` - simple API for Steam's Web API with automatic population of interfaces
* :doc:`WebAuth <api/steam.webauth>` - authentication for access to ``store.steampowered.com`` and ``steamcommunity.com``

Checkout the :doc:`user_guide` for examples, or the :doc:`api/steam` for details.

For questions, issues, or general curiosity, visit the repo at `https://github.com/ValvePython/steam <https://github.com/ValvePython/steam>`_.

Quick install
=============

For system specific details, see :doc:`install`.

Install latest version from PYPI::

    pip install -U steam

Install the current dev version from ``github``::

    pip install git+https://github.com/ValvePython/steam
