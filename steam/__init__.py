__version__ = "0.8.0"
__author__ = "Rossen Georgiev"

version_info = (0, 8, 0)

from steam.steamid import SteamID
from steam.webapi import WebAPI
from steam.webauth import WebAuth


# proxy object
# avoids importing steam.enums.emsg unless it's needed
class SteamClient(object):
    def __new__(cls, *args, **kwargs):
        from steam.client import SteamClient as SC

        bases = cls.__bases__

        if bases != (object, ):
            if bases[0] != SteamClient:
                raise ValueError("SteamClient needs to be the first base for custom classes")

            SC = type("SteamClient", (SC,) + bases[1:], {})

        return SC(*args, **kwargs)
