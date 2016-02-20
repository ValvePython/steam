.. include:: global.rst

Quick start
***********

Welcome to the quick start section.
The aim here is to give you a very quick
overview of the functionality available in the ``steam`` module.

SteamID
=======

``SteamID`` object can be used to convert the universal steam id
to its' various representations.

.. note::
    ``SteamID`` is immutable as it inherits from ``int``.

Example usage
-------------

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
    >>> group = SteamID('[g:1:4]')
    >>> group.id  # accountid
    4
    >>> group.as_32  # accountid
    4
    >>> group.as_64
    103582791429521412
    >>> int(group)
    103582791429521412
    >>> str(group)
    '103582791429521412'
    >>> group.as_steam2 # only works for 'Individual' accounts
    'STEAM_1:0:2'
    >>> group.as_steam3
    '[g:1:4]'
    >>> group.community_url
    'https://steamcommunity.com/gid/103582791429521412'


Resolving community urls to ``SteamID``
-----------------------------------------

The ``steamid`` submodule provides function to resolve community urls.
Here are some examples:

.. code:: python

    >>> steam.steamid.from_url('https://steamcommunity.com/id/drunkenf00l')
    >>> steam.steamid.from_url('http://steamcommunity.com/profiles/76561197968459473')
    SteamID(id=8193745, type='Individual', universe='Public', instance=1)

    >>> steam.steamid.steam64_from_url('http://steamcommunity.com/profiles/76561197968459473')
    '76561197968459473'


WebAPI
======

Wrapper around `Steam Web API`_. Requires `API Key`_. Upon initialization the
instance will fetch all available interfaces from the API and populate the namespace.

.. note::
   Interface availability depends on the ``key``.
   Unless data is loaded manually.

Example usage
-------------

.. code:: python

    >>> from steam import WebAPI
    >>> api = WebAPI(key="<your api key>")

    # instance.<interface>.<method>
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
``key``, ``format``, ``raw``, ``http_timeout`` parameters can be specified on ``WebAPI`` to affect
all method calls, or when calling a specific method.
Some methods have parameters which need to be a ``list``.
Trying to call nonexistent method will raise an ``AttributeError``.

Supported formats by web api are: ``json`` (default), ``vdf``, ``xml``
The response will be deserialized using the appropriate module unless ``raw`` is
``True``.

WebAPI documentation
--------------------

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


For a more complete list of all available interfaces and methods visit:
https://lab.xpaw.me/steam_api_documentation.html


SteamClient
===========

``gevent`` based implementation for interacting with the Steam network.
This is currently a WIP, and is barebone.
It should be possible to implement various functions with ease.

.. warning::
    API for this part could change without notice

CLI example
-----------

This program will prompt for user and password.
If authentication code is required, it will additionally prompt for that.
Configuring logging will lets us see the internal interactions.

.. code:: python

    import logging
    from getpass import getpass
    logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

    from steam import SteamClient
    from steam.enums import EResult
    from steam.enums.emsg import EMsg

    client = SteamClient()
    #client.cm.verbose_debug = True

    @client.on('error')
    def print_error(result):
        print "Error:", EResult(result)

    @client.on('auth_code_required')
    def auth_code_prompt(is_2fa, code_mismatch):
        if is_2fa:
            code = raw_input("Enter 2FA Code: ")
            logOnDetails.update({'two_factor_code': code})
        else:
            code = raw_input("Enter Email Code: ")
            logOnDetails.update({'auth_code': code})

        client.login(**logOnDetails)

    logOnDetails = {
        'username': raw_input("Steam user: "),
        'password': getpass("Password: "),
    }

    client.login(**logOnDetails)
    # OR
    # client.anonymous_login()

    msg, = client.wait_event(EMsg.ClientAccountInfo)
    print "Logged on as: %s" % msg.body.persona_name
    print "SteamID: %s" % repr(client.steamid)

    client.wait_event('disconnect')


Sending a message
-----------------

Example of sending a protobuf message and handling the response.
`wait_event` will block until specified event.

.. code:: python

    from steam.core.emsg import MsgProto

    message = MsgProto(EMsg.ClientRequestWebAPIAuthenticateUserNonce)
    client.send(message)

    resp, = client.wait_event(EMsg.ClientRequestWebAPIAuthenticateUserNonceResponse)

    if resp.body.eresult == EResult.OK:
        print "WebAPI Nonce: %s" % repr(resp.body.webapi_authenticate_user_nonce)
    else:
        print "Error: %s" % EResult(resp.body.eresult)


Alternatively, a callback can be registered to handle the response event every time.

.. code:: python

    @client.on(EMsg.ClientRequestWebAPIAuthenticateUserNonceResponse)
    def handle_webapi_nonce(msg):
        print "WebAPI Nonce: %s" % repr(resp.body.webapi_authenticate_user_nonce)

    # OR
    client.on(EMsg.ClientRequestWebAPIAuthenticateUserNonceResponse, handle_webapi_nonce)
