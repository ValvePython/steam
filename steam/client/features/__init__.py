"""
All high level features of :class:`steam.client.SteamClient` are here in seperate submodules.
"""
from steam.client.features.misc import Misc
from steam.client.features.user import User

class FeatureBase(Misc, User):
    """
    This object is used as base to implement all high level functionality.
    The features are seperated into submodules.
    """
    pass
