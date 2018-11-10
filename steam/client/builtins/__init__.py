"""
All high level features of :class:`steam.client.SteamClient` are implemented here in separate submodules.
"""
from steam.client.builtins.account import Account
from steam.client.builtins.user import User
from steam.client.builtins.web import Web
from steam.client.builtins.unified_messages import UnifiedMessages
from steam.client.builtins.leaderboards import Leaderboards
from steam.client.builtins.gameservers import GameServers
from steam.client.builtins.friends import Friends
from steam.client.builtins.apps import Apps

class BuiltinBase(GameServers, UnifiedMessages, Account, User, Web, Leaderboards, Friends, Apps):
    """
    This object is used as base to implement all high level functionality.
    The features are separated into submodules.
    """
    pass
