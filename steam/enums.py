import enum


class EResult(enum.Enum):
    OK = 1                              # success
    Fail = 2                            # generic failure
    NoConnection = 3                    # no/failed network connection
    sultNoConnectionRetry = 4           # OBSOLETE - removed
    InvalidPassword = 5                 # password/ticket is invalid
    LoggedInElsewhere = 6               # same user logged in elsewhere
    InvalidProtocolVer = 7              # protocol version is incorrect
    InvalidParam = 8                    # a parameter is incorrect
    FileNotFound = 9                    # file was not found
    Busy = 10                           # called method busy - action not taken
    InvalidState = 11                   # called object was in an invalid state
    InvalidName = 12                    # name is invalid
    InvalidEmail = 13                   # email is invalid
    DuplicateName = 14                  # name is not unique
    AccessDenied = 15                   # access is denied
    Timeout = 16                        # operation timed out
    Banned = 17                         # VAC2 banned
    AccountNotFound = 18                # account not found
    InvalidSteamID = 19                 # steamID is invalid
    ServiceUnavailable = 20             # The requested service is currently unavailable
    NotLoggedOn = 21                    # The user is not logged on
    Pending = 22                        # Request is pending (may be in process, or waiting on third party)
    EncryptionFailure = 23              # Encryption or Decryption failed
    InsufficientPrivilege = 24          # Insufficient privilege
    LimitExceeded = 25                  # Too much of a good thing
    Revoked = 26                        # Access has been revoked (used for revoked guest passes)
    Expired = 27                        # License/Guest pass the user is trying to access is expired
    AlreadyRedeemed = 28                # Guest pass has already been redeemed by account, cannot be acked again
    DuplicateRequest = 29               # The request is a duplicate and the action has already occurred in the past, ignored this time
    AlreadyOwned = 30                   # All the games in this guest pass redemption request are already owned by the user
    IPNotFound = 31                     # IP address not found
    PersistFailed = 32                  # failed to write change to the data store
    LockingFailed = 33                  # failed to acquire access lock for this operation
    LogonSessionReplaced = 34,
    ConnectFailed = 35,
    HandshakeFailed = 36,
    IOFailure = 37,
    RemoteDisconnect = 38,
    ShoppingCartNotFound = 39           # failed to find the shopping cart requested
    Blocked = 40                        # a user didn't allow it
    Ignored = 41                        # target is ignoring sender
    NoMatch = 42                        # nothing matching the request found
    AccountDisabled = 43,
    ServiceReadOnly = 44                # this service is not accepting content changes right now
    AccountNotFeatured = 45             # account doesn't have value, so this feature isn't available
    AdministratorOK = 46                # allowed to take this action, but only because requester is admin
    ContentVersion = 47                 # A Version mismatch in content transmitted within the Steam protocol.
    TryAnotherCM = 48                   # The current CM can't service the user making a request, user should try another.
    PasswordRequiredToKickSession = 49  # You are already logged in elsewhere, this cached credential login has failed.
    AlreadyLoggedInElsewhere = 50       # You are already logged in elsewhere, you must wait
    Suspended = 51,
    Cancelled = 52,
    DataCorruption = 53,
    DiskFull = 54,
    RemoteCallFailed = 55,


class EUniverse(enum.Enum):
    Invalid = 0
    Public = 1
    Beta = 2
    Internal = 3
    Dev = 4


class EType(enum.Enum):
    Invalid = 0
    Individual = 1
    Multiseat = 2
    GameServer = 3
    AnonGameServer = 4
    Pending = 5
    ContentServer = 6
    Clan = 7
    Chat = 8
    ConsoleUser = 9
    AnonUser = 10


class EServerType(enum.Enum):
    Invalid = -1
    Shell = 0
    GM = 1
    BUM = 2
    AM = 3
    BS = 4
    VS = 5
    ATS = 6
    CM = 7
    FBS = 8
    FG = 9
    SS = 10
    DRMS = 11
    HubOBSOLETE = 12
    Console = 13
    ASBOBSOLETE = 14
    Client = 15
    BootstrapOBSOLETE = 16
    DP = 17
    WG = 18
    SM = 19
    UFS = 21
    Util = 23
    DSS = 24
    P2PRelayOBSOLETE = 25
    AppInformation = 26
    Spare = 27
    FTS = 28
    EPM = 29
    PS = 30
    IS = 31
    CCS = 32
    DFS = 33
    LBS = 34
    MDS = 35
    CS = 36
    GC = 37
    NS = 38
    OGS = 39
    WebAPI = 40
    UDS = 41
    MMS = 42
    GMS = 43
    KGS = 44
    UCM = 45
    RM = 46
    FS = 47
    Econ = 48
    Backpack = 49
    Max = 50
