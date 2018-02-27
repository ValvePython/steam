__version__ = "0.9.0"
__author__ = "Rossen Georgiev"

version_info = tuple(map(int, __version__.split('.')))

from steam.steamid import SteamID
from steam.globalid import GlobalID
from steam.webapi import WebAPI
from steam.webauth import WebAuth, MobileWebAuth


# proxy object
# avoids importing steam.enums.emsg unless it's needed
# avoids gevent monkey patching
class SteamClient(object):
    def __new__(cls, *args, **kwargs):
        from steam.client import SteamClient as SC

        bases = cls.__bases__

        if bases != (object, ):
            if bases[0] != SteamClient:
                raise ValueError("SteamClient needs to be the first base for custom classes")

            SC = type("SteamClient", (SC,) + bases[1:], {})

        return SC(*args, **kwargs)
