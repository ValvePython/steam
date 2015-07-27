|pypi| |license| |coverage| |master_build|

Module for interacting with various Steam_ features

WebAPI
------

Wrapper around `Steam Web API`_. Requires `API Key`_. Upon initialization the
instance will fetch all available interfaces from the API and populate the namespace.
What interfaces are availability depends on the ``key``.

.. code:: python

    >>> from steam import WebAPI
    >>> api = WebAPI(key="<your api key>")

    >>> api.ISteamWebAPIUtil.GetServerInfo()
    >>> api.call('ISteamWebAPIUtil.GetServerInfo')
    {u'servertimestring': u'Sun Jul 05 22:37:25 2015', u'servertime': 1436161045}

    >>> api.ISteamUser.ResolveVanityURL(vanityurl="valve", url_type=2)
    >>> api.call('ISteamUser.ResolveVanityURL', vanityurl="valve", url_type=2)
    {u'response': {u'steamid': u'103582791429521412', u'success': 1}}

    # call a specific version of the method
    >>> api.ISteamUser.ResolveVanityURL_v1(vanityurl="valve", url_type=2)
    >>> api.call('ISteamUser.ResolveVanityURL_v1', vanityurl="valve", url_type=2)

It's not necessary to provide the key when calling any interface method.
``key``, ``format``, ``raw`` parameters can be specified on ``WebAPI`` to affect
all method calls, or when calling a specific method.
Some methods have parameters which need to be a ``list``.
Trying to call nonexistent method will raise an ``AttributeError``.

Supported formats by web api are: ``json`` (default), ``vdf``, ``xml``
The response will be deserialized using the appropriate module unless ``raw`` is
``True``.

.. code:: python

    >>> api.ISteamUser.ResolveVanityURL.__doc__  # method doc
    """
    ResolveVanityURL (v0001)

      Parameters:
        key                       string   required
          - access key
        url_type                  int32    optional
          - The type of vanity URL. 1 (default): Individual profile, 2: Group, 3: Official game group
        vanityurl                 string   required
          - The vanity URL to get a SteamID for

    """

    # or calling doc() will print it
    >>> api.ISteamUser.ResolveVanityURL.doc()  # method doc
    >>> api.ISteamUser.doc()  # interface and all methods
    >>> api.doc()  # all available interfaces


Checkout the wiki for a `list of the currently available API interfaces`_.


SteamID
-------

.. code:: python

    >>> from steam import SteamID

    >>> SteamID()
    SteamID(id=0, type='Invalid', universe='Invalid', instance=0)

    >>> SteamID(12345)  # accountid
    >>> SteamID('12345')
    >>> SteamID('STEAM_1:1:6172')  # steam2
    SteamID(id=12345, type='Individual', universe='Public', instance=1)

    >>> SteamID(103582791429521412)  # steam64
    >>> SteamID('103582791429521412')
    >>> SteamID('[g:1:4]')  # steam3
    SteamID(id=4, type='Clan', universe='Public', instance=0)

    # vanity urls are resolved by fetching the community profile page (this is unstable)
    # use the WebAPI to reliably resolve vanity urls
    >>> SteamID('https://steamcommunity.com/id/drunkenf00l')
    >>> SteamID('http://steamcommunity.com/profiles/76561197968459473')  # no request is made
    SteamID(id=8193745, type='Individual', universe='Public', instance=1)

    >>> group = SteamID('[g:1:4]')
    >>> group.id  # accountid
    4
    >>> group.as_32  # accountid
    4
    >>> group.as_64
    103582791429521412
    >>> str(group)
    '103582791429521412'
    >>> group.as_steam2 # only works for 'Individual' accounts
    'STEAM_1:0:2'
    >>> group.as_steam3
    '[g:1:4]'
    >>> group.community_url
    'https://steamcommunity.com/gid/103582791429521412'


.. _Steam: https://store.steampowered.com/
.. _Steam Web API: https://developer.valvesoftware.com/wiki/Steam_Web_API
.. _API Key: http://steamcommunity.com/dev/apikey
.. _list of the currently available API interfaces: https://github.com/ValvePython/steam/wiki/web-api

.. |pypi| image:: https://img.shields.io/pypi/v/steam.svg?style=flat&label=latest%20version
    :target: https://pypi.python.org/pypi/steam
    :alt: Latest version released on PyPi

.. |license| image:: https://img.shields.io/pypi/l/steam.svg?style=flat&label=license
    :target: https://pypi.python.org/pypi/steam
    :alt: MIT License

.. |coverage| image:: https://img.shields.io/coveralls/ValvePython/steam/master.svg?style=flat
    :target: https://coveralls.io/r/ValvePython/steam?branch=master
    :alt: Test coverage

.. |master_build| image:: https://img.shields.io/travis/ValvePython/steam/master.svg?style=flat&label=master
    :target: http://travis-ci.org/ValvePython/steam
    :alt: Build status of master branch
