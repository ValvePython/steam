Module for interacting with various Steam_ features

SteamID
-------------

.. code:: python

    >>> from steam import SteamID

    >>> SteamID()
    SteamID(id=0, type='Invalid', universe='Invalid', instance=0)

    >>> SteamID(12345)  # accountid
    >>> SteamID('12345')
    SteamID(id=12345, type='Individual', universe='Public', instance=1)

    >>> SteamID(103582791429521412)  # steam64
    >>> SteamID('103582791429521412')
    >>> SteamID('[g:1:4]')  # steam3
    SteamID(id=4, type='Clan', universe='Public', instance=0)

    # vanity urls are resolved by making an HTTP request
    >>> SteamID('https://steamcommunity.com/id/drunkenf00l')
    >>> SteamID('http://steamcommunity.com/profiles/76561197968459473')  # no request is made
    SteamID(id=8193745, type='Individual', universe='Public', instance=1)


.. _Steam: http://steampowered.com/
