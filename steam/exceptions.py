
from steam.enums import EResult

class SteamError(Exception):
    def __init__(self, message, eresult=EResult.Fail):
        Exception.__init__(self, message)
        self.eresult = EResult(eresult)  #: :class:`.EResult`
