"""
All high level features of :class:`steam.client.SteamClient` are implemented here in separate submodules.
"""
from steam.client.builtins.misc import Misc
from steam.client.builtins.user import User
from steam.client.builtins.web import Web
from steam.client.builtins.unified_messages import UnifiedMessages
from steam.client.builtins.leaderboards import Leaderboards

class BuiltinBase(Misc, User, Web, UnifiedMessages, Leaderboards):
    """
    This object is used as base to implement all high level functionality.
    The features are separated into submodules.
    """
    pass
