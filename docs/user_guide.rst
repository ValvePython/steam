.. include:: global.rst

User guide
**********

Welcome to the quick start section.
The aim here is to give you a very quick
overview of the functionality available in the ``steam`` module.

SteamID
=======

:mod:`SteamID <steam.steamid.SteamID>` can be used to convert the universal steam id
to its' various representations.

.. note::
    :class:`SteamID <steam.steamid.SteamID>` is immutable as it inherits from :class:`int`.

Converting between representations
----------------------------------

.. code:: python

    >>> from steam.steamid import SteamID

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


Resolving community urls to :class:`SteamID <steam.steamid.SteamID>`
--------------------------------------------------------------------

The :mod:`steam.steamid` submodule provides function to resolve community urls.
Here are some examples:

.. code:: python

    >>> SteamID.from_url('https://steamcommunity.com/id/drunkenf00l')
    >>> steam.steamid.from_url('https://steamcommunity.com/id/drunkenf00l')
    SteamID(id=8193745, type='Individual', universe='Public', instance=1)

    >>> steam.steamid.steam64_from_url('http://steamcommunity.com/profiles/76561197968459473')
    '76561197968459473'


WebAPI
======

:mod:`WebAPI <steam.webapi>` is a thin Wrapper around `Steam Web API`_. Requires `API Key`_. Upon initialization the
instance will fetch all available interfaces and populate the namespace.

Obtaining a key
---------------

Any steam user can get a key by visiting http://steamcommunity.com/dev/apikey.
The only requirement is that the user has verified their email.
Then the key can be used on the ``public`` WebAPI. See :class:`steam.webapi.APIHost`

.. note::
   Interface availability depends on the ``key``.
   Unless the schema is loaded manually.

Calling an endpoint
-------------------

.. code:: python

    >>> from steam.webapi import WebAPI
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
https://steamapi.xpaw.me/


SteamClient
===========

``gevent`` based implementation for interacting with the Steam network.
The library comes with some Steam client features implemented, see :doc:`api/steam.client` for more details.

.. warning::
    :class:`.SteamClient` no longer applies gevent monkey patches by default.
    See :mod:`steam.monkey` for details how make stdlib gevent cooperative.

CLI example
-----------

In this example, the user will be prompted for credential and once logged in will the account name.
After that we logout.

.. code:: python

    from steam.client import SteamClient
    from steam.enums.emsg import EMsg

    client = SteamClient()

    @client.on(EMsg.ClientVACBanStatus)
    def print_vac_status(msg):
        print("Number of VAC Bans: %s" % msg.body.numBans)

    client.cli_login()

    print("Logged on as: %s" % client.user.name)
    print("Community profile: %s" % client.steam_id.community_url)
    print("Last logon: %s" % client.user.last_logon)
    print("Last logoff: %s" % client.user.last_logoff)
    print("Number of friends: %d" % len(client.friends))

    client.logout()

You can find more examples at https://github.com/ValvePython/steam/tree/master/recipes

Sending a message
-----------------

Example of sending a protobuf message and handling the response.
:meth:`send_message_and_wait() <steam.client.SteamClient.send_message_and_wait>` will send a message and block until the specified event.

.. code:: python

    from steam.enums import EResult
    from steam.core.msg import MsgProto
    from steam.enums.emsg import EMsg

    message = MsgProto(EMsg.ClientAddFriend)
    message.body.steamid_to_add = 76561197960265728

    resp = client.send_message_and_wait(message, EMsg.ClientAddFriendResponse)

    if resp.eresult == EResult.OK:
        print "Send a friend request to %s (%d)" % (repr(resp.body.persona_name_added),
                                                   resp.body.steam_id_added,
                                                   )
    else:
        print "Error: %s" % EResult(resp.eresult)


Alternatively, a callback can be registered to handle the response event every time.

.. code:: python

    @client.on(EMsg.ClientAddFriendResponse)
    def handle_add_response(msg):
        pass
    # OR
    client.on(EMsg.ClientAddFriendResponse, handle_add_response)


Logging
-------

It is often useful to see the message that are coming in and going on.
Here is how to enable debug logging to the console.

.. code:: python

    import logging
    logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

For more complicated :mod:`logging` configurations, consult the python documentation.

By default the :class:`.SteamClient` will not log the contents of messages.
To enable that simply set :attr:`.SteamClient.verbose_debug` to ``True`` on your :class:`.SteamClient` instance.

.. code:: python

    client = SteamClient()
    client.verbose_debug = True

When there are multiple instances, they will all log under the same logger name.
We can override the default logger instances with new one and give it a different name.

.. code:: python

    client1 = SteamClient()
    client2 = SteamClient()

    client1._LOG = logging.getLogger("SC#1")
    client2._LOG = logging.getLogger("SC#2")

Web Authentication
==================

There are currently two paths for gaining access to steam websites.
Either using :class:`WebAuth <steam.webauth.WebAuth>`, or via a :meth:`SteamClient.get_web_session() <steam.client.builtins.web.Web.get_web_session>` instance.

.. code:: python

    session = client.get_web_session()  # returns requests.Session
    session.get('https://store.steampowered.com')

For more details about :class:`WebAuth <steam.webauth.WebAuth>`, see :mod:`steam.webauth`
