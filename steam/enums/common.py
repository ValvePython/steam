from steam.enums.base import SteamIntEnum


class EResult(SteamIntEnum):
    Invalid = 0
    OK = 1
    Fail = 2
    NoConnection = 3
    InvalidPassword = 5
    LoggedInElsewhere = 6
    InvalidProtocolVer = 7
    InvalidParam = 8
    FileNotFound = 9
    Busy = 10
    InvalidState = 11
    InvalidName = 12
    InvalidEmail = 13
    DuplicateName = 14
    AccessDenied = 15
    Timeout = 16
    Banned = 17
    AccountNotFound = 18
    InvalidSteamID = 19
    ServiceUnavailable = 20
    NotLoggedOn = 21
    Pending = 22
    EncryptionFailure = 23
    InsufficientPrivilege = 24
    LimitExceeded = 25
    Revoked = 26
    Expired = 27
    AlreadyRedeemed = 28
    DuplicateRequest = 29
    AlreadyOwned = 30
    IPNotFound = 31
    PersistFailed = 32
    LockingFailed = 33
    LogonSessionReplaced = 34
    ConnectFailed = 35
    HandshakeFailed = 36
    IOFailure = 37
    RemoteDisconnect = 38
    ShoppingCartNotFound = 39
    Blocked = 40
    Ignored = 41
    NoMatch = 42
    AccountDisabled = 43
    ServiceReadOnly = 44
    AccountNotFeatured = 45
    AdministratorOK = 46
    ContentVersion = 47
    TryAnotherCM = 48
    PasswordRequiredToKickSession = 49
    AlreadyLoggedInElsewhere = 50
    Suspended = 51
    Cancelled = 52
    DataCorruption = 53
    DiskFull = 54
    RemoteCallFailed = 55
    PasswordUnset = 56
    ExternalAccountUnlinked = 57
    PSNTicketInvalid = 58
    ExternalAccountAlreadyLinked = 59
    RemoteFileConflict = 60
    IllegalPassword = 61
    SameAsPreviousValue = 62
    AccountLogonDenied = 63
    CannotUseOldPassword = 64
    InvalidLoginAuthCode = 65
    AccountLogonDeniedNoMail = 66
    HardwareNotCapableOfIPT = 67
    IPTInitError = 68
    ParentalControlRestricted = 69
    FacebookQueryError = 70
    ExpiredLoginAuthCode = 71
    IPLoginRestrictionFailed = 72
    AccountLockedDown = 73
    AccountLogonDeniedVerifiedEmailRequired = 74
    NoMatchingURL = 75
    BadResponse = 76
    RequirePasswordReEntry = 77
    ValueOutOfRange = 78
    UnexpectedError = 79
    Disabled = 80
    InvalidCEGSubmission = 81
    RestrictedDevice = 82
    RegionLocked = 83
    RateLimitExceeded = 84
    AccountLoginDeniedNeedTwoFactor = 85
    ItemDeleted = 86
    AccountLoginDeniedThrottle = 87
    TwoFactorCodeMismatch = 88
    TwoFactorActivationCodeMismatch = 89
    AccountAssociatedToMultiplePartners = 90
    NotModified = 91
    NoMobileDevice = 92
    TimeNotSynced = 93
    SMSCodeFailed = 94
    AccountLimitExceeded = 95
    AccountActivityLimitExceeded = 96
    PhoneActivityLimitExceeded = 97
    RefundToWallet = 98
    EmailSendFailure = 99
    NotSettled = 100
    NeedCaptcha = 101
    GSLTDenied = 102
    GSOwnerDenied = 103
    InvalidItemType = 104


class EUniverse(SteamIntEnum):
    Invalid = 0
    Public = 1
    Beta = 2
    Internal = 3
    Dev = 4
    Max = 5


class EType(SteamIntEnum):
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
    Max = 11


class EServerType(SteamIntEnum):
    Invalid = -1
    First = 0
    GM = 1
    BUM = 2
    AM = 3
    BS = 4
    VS = 5
    ATS = 6
    CM = 7
    FBS = 8
    BoxMonitor = 9
    SS = 10
    DRMS = 11
    HubOBSOLETE = 12
    Console = 13
    PICS = 14
    Client = 15
    BootstrapOBSOLETE = 16
    DP = 17
    WG = 18
    SM = 19
    UFS = 21
    Util = 23
    DSS = 24
    Community = 24
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
    UGS = 50
    Store = 51
    MoneyStats = 52
    CRE = 53
    UMQ = 54
    Workshop = 55
    BRP = 56
    GCH = 57
    MPAS = 58
    Trade = 59
    Secrets = 60
    Logsink = 61
    Market = 62
    Quest = 63
    WDS = 64
    ACS = 65
    PNP = 66
    Max = 67


class EOSType(SteamIntEnum):
    Unknown = -1
    UMQ = -400

    PS3 = -300

    MacOSUnknown = -102
    MacOS104 = -101
    MacOS105 = -100
    MacOS1058 = -99
    MacOS106 = -95
    MacOS1063 = -94
    MacOS1064_slgu = -93
    MacOS1067 = -92
    MacOS107 = -90
    MacOS108 = -89
    MacOS109 = -88
    MacOS1010 = -87

    LinuxUnknown = -203
    Linux22 = -202
    Linux24 = -201
    Linux26 = -200
    Linux32 = -199
    Linux35 = -198
    Linux36 = -197
    Linux310 = -196

    WinUnknown = 0
    Win311 = 1
    Win95 = 2
    Win98 = 3
    WinME = 4
    WinNT = 5
    Win200 = 6
    WinXP = 7
    Win2003 = 8
    WinVista = 9
    Win7 = 10
    Win2008 = 11
    Win2012 = 12
    Win8 = 13
    Win81 = 14
    Win2012R2 = 15
    Win10 = 16

    WinMAX = 15

    Max = 26


class EPersonaState(SteamIntEnum):
    Offline = 0
    Online = 1
    Busy = 2
    Away = 3
    Snooze = 4
    LookingToTrade = 5
    LookingToPlay = 6
    Max = 7


class EFriendRelationship(SteamIntEnum):
    No = 0
    Blocked = 1
    RequestRecipient = 2
    Friend = 3
    RequestInitiator = 4
    Ignored = 5
    IgnoredFriend = 6
    SuggestedFriend = 7
    Max = 8


class EAccountFlags(SteamIntEnum):
    NormalUser = 0
    PersonaNameSet = 1
    Unbannable = 2
    PasswordSet = 4
    Support = 8
    Admin = 16
    Supervisor = 32
    AppEditor = 64
    HWIDSet = 128
    PersonalQASet = 256
    VacBeta = 512
    Debug = 1024
    Disabled = 2048
    LimitedUser = 4096
    LimitedUserForce = 8192
    EmailValidated = 16384
    MarketingTreatment = 32768
    OGGInviteOptOut = 65536
    ForcePasswordChange = 131072
    ForceEmailVerification = 262144
    LogonExtraSecurity = 524288
    LogonExtraSecurityDisabled = 1048576
    Steam2MigrationComplete = 2097152
    NeedLogs = 4194304
    Lockdown = 8388608
    MasterAppEditor = 16777216
    BannedFromWebAPI = 33554432
    ClansOnlyFromFriends = 67108864
    GlobalModerator = 134217728

class EFriendFlags(SteamIntEnum):
    No = 0
    Blocked = 1
    FriendshipRequested = 2
    Immediate = 4
    ClanMember = 8
    OnGameServer = 16
    RequestingFriendship = 128
    RequestingInfo = 256
    Ignored = 512
    IgnoredFriend = 1024
    Suggested = 2048
    FlagAll = 65535


class EPersonaStateFlag(SteamIntEnum):
    HasRichPresence = 1
    InJoinableGame = 2
    OnlineUsingWeb = 256
    OnlineUsingMobile = 512
    OnlineUsingBigPicture = 1024


class EClientPersonaStateFlag(SteamIntEnum):
    Status = 1
    PlayerName = 2
    QueryPort = 4
    SourceID = 8
    Presence = 16
    Metadata = 32
    LastSeen = 64
    ClanInfo = 128
    GameExtraInfo = 256
    GameDataBlob = 512
    ClanTag = 1024
    Facebook = 2048


# Do not remove
from sys import modules
from enum import EnumMeta

__all__ = list(map(lambda y: y.__name__,
              filter(lambda x: x.__class__ is EnumMeta, modules[__name__].__dict__.values()),
              ))

del modules, EnumMeta
