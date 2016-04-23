"""
All high level features of :class:`steam.client.SteamClient` are implemented here in seperate submodules.
"""
from steam.client.builtins.misc import Misc
from steam.client.builtins.user import User
from steam.client.builtins.web import Web

class BuiltinBase(Misc, User, Web):
    """
    This object is used as base to implement all high level functionality.
    The features are seperated into submodules.
    """
    pass
