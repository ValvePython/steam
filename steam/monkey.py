"""
Helper moduel for calling ``gevent`` monkey patch functions.
This only need to if want to make stdlib gevent cooperative.
The patches need to be applied before any other module imports.

See :mod:`gevent.monkey` for details

.. code:: python

    import steam.monkey
    steam.monkey.patch_minimal()

    import requests
    from steam.client import SteamClient, EMsg
"""

def patch_minimal():
    """
    This method needs to be called before any other imports

    It calls :meth:`gevent.monkey.patch_socket()` and :meth:`gevent.monkey.patch_ssl()`
    """
    import gevent.monkey
    gevent.monkey.patch_socket()
    gevent.monkey.patch_ssl()
    gevent.monkey.patch_dns()
