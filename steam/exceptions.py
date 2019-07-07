
from steam.enums import EResult

class SteamError(Exception):
    def __init__(self, message, eresult=EResult.Fail):
        Exception.__init__(self, message, eresult)
        self.message = message
        self.eresult = EResult(eresult)  #: :class:`.EResult`

    def __str__(self):
        return "(%s) %s" % (self.eresult, self.message)
