
from steam.enums import EResult

class SteamError(Exception):
    """ General error that also carries EResult code """
    def __init__(self, message, eresult=EResult.Fail):
        Exception.__init__(self, message, eresult)
        self.message = message
        self.eresult = EResult(eresult)  #: :class:`.EResult`

    def __str__(self):
        return "(%s) %s" % (self.eresult, self.message)

class ManifestError(SteamError):
    """
    Raised when there a problem getting a manifest by :class:`CDNClient`
    Encapsulates original exception in :attr:`.error` and includes manifest details
    """
    def __init__(self, message, app_id, depot_id, manifest_gid, error=None):
        self.message = message
        self.app_id = app_id
        self.depot_id = depot_id
        self.manifest_gid = manifest_gid
        self.error = error

        if isinstance(error, SteamError):
            self.eresult = error.eresult
        else:
            self.eresult = EResult.Fail

    def __repr__(self):
        return "%s(%s, app=%s, depot=%s, manifest=%s, error=%s)" % (
            self.__class__.__name__,
            repr(self.message),
            self.app_id,
            self.depot_id,
            self.manifest_gid,
            repr(self.error),
        )

    def __str__(self):
        return "(%s) %s (app=%s depot=%s manifest=%s)" % (
            self.eresult,
            self.message,
            self.app_id,
            self.depot_id,
            self.manifest_gid,
        )

