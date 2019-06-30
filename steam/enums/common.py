from steam.enums.base import SteamIntEnum


class EResult(SteamIntEnum):
    Invalid = 0
    OK = 1                              #: success
    Fail = 2                            #: generic failure
    NoConnection = 3                    #: no/failed network connection
#   NoConnectionRetry = 4               #: OBSOLETE - removed
    InvalidPassword = 5                 #: password/ticket is invalid
    LoggedInElsewhere = 6               #: same user logged in elsewhere
    InvalidProtocolVer = 7              #: protocol version is incorrect
    InvalidParam = 8                    #: a parameter is incorrect
    FileNotFound = 9                    #: file was not found
    Busy = 10                           #: called method busy - action not taken
    InvalidState = 11                   #: called object was in an invalid state
    InvalidName = 12                    #: name is invalid
    InvalidEmail = 13                   #: email is invalid
    DuplicateName = 14                  #: name is not unique
    AccessDenied = 15                   #: access is denied
    Timeout = 16                        #: operation timed out
    Banned = 17                         #: VAC2 banned
    AccountNotFound = 18                #: account not found
    InvalidSteamID = 19                 #: steamID is invalid
    ServiceUnavailable = 20             #: The requested service is currently unavailable
    NotLoggedOn = 21                    #: The user is not logged on
    Pending = 22                        #: Request is pending (may be in process, or waiting on third party)
    EncryptionFailure = 23              #: Encryption or Decryption failed
    InsufficientPrivilege = 24          #: Insufficient privilege
    LimitExceeded = 25                  #: Too much of a good thing
    Revoked = 26                        #: Access has been revoked (used for revoked guest passes)
    Expired = 27                        #: License/Guest pass the user is trying to access is expired
    AlreadyRedeemed = 28                #: Guest pass has already been redeemed by account, cannot be acked again
    DuplicateRequest = 29               #: The request is a duplicate and the action has already occurred in the past, ignored this time
    AlreadyOwned = 30                   #: All the games in this guest pass redemption request are already owned by the user
    IPNotFound = 31                     #: IP address not found
    PersistFailed = 32                  #: failed to write change to the data store
    LockingFailed = 33                  #: failed to acquire access lock for this operation
    LogonSessionReplaced = 34
    ConnectFailed = 35
    HandshakeFailed = 36
    IOFailure = 37
    RemoteDisconnect = 38
    ShoppingCartNotFound = 39           #: failed to find the shopping cart requested
    Blocked = 40                        #: a user didn't allow it
    Ignored = 41                        #: target is ignoring sender
    NoMatch = 42                        #: nothing matching the request found
    AccountDisabled = 43
    ServiceReadOnly = 44                #: this service is not accepting content changes right now
    AccountNotFeatured = 45             #: account doesn't have value, so this feature isn't available
    AdministratorOK = 46                #: allowed to take this action, but only because requester is admin
    ContentVersion = 47                 #: A Version mismatch in content transmitted within the Steam protocol.
    TryAnotherCM = 48                   #: The current CM can't service the user making a request, user should try another.
    PasswordRequiredToKickSession = 49  #: You are already logged in elsewhere, this cached credential login has failed.
    AlreadyLoggedInElsewhere = 50       #: You are already logged in elsewhere, you must wait
    Suspended = 51                      #: Long running operation (content download) suspended/paused
    Cancelled = 52                      #: Operation canceled (typically by user: content download)
    DataCorruption = 53                 #: Operation canceled because data is ill formed or unrecoverable
    DiskFull = 54                       #: Operation canceled - not enough disk space.
    RemoteCallFailed = 55               #: an remote call or IPC call failed
    PasswordUnset = 56                  #: Password could not be verified as it's unset server side
    ExternalAccountUnlinked = 57        #: External account (PSN, Facebook...) is not linked to a Steam account
    PSNTicketInvalid = 58               #: PSN ticket was invalid
    ExternalAccountAlreadyLinked = 59   #: External account (PSN, Facebook...) is already linked to some other account, must explicitly request to replace/delete the link first
    RemoteFileConflict = 60             #: The sync cannot resume due to a conflict between the local and remote files
    IllegalPassword = 61                #: The requested new password is not legal
    SameAsPreviousValue = 62            #: new value is the same as the old one ( secret question and answer )
    AccountLogonDenied = 63             #: account login denied due to 2nd factor authentication failure
    CannotUseOldPassword = 64           #: The requested new password is not legal
    InvalidLoginAuthCode = 65           #: account login denied due to auth code invalid
    AccountLogonDeniedNoMail = 66       #: account login denied due to 2nd factor auth failure - and no mail has been sent
    HardwareNotCapableOfIPT = 67
    IPTInitError = 68
    ParentalControlRestricted = 69      #: operation failed due to parental control restrictions for current user
    FacebookQueryError = 70             #: Facebook query returned an error
    ExpiredLoginAuthCode = 71           #: account login denied due to auth code expired
    IPLoginRestrictionFailed = 72
    AccountLockedDown = 73
    AccountLogonDeniedVerifiedEmailRequired = 74
    NoMatchingURL = 75
    BadResponse = 76                          #: parse failure, missing field, etc.
    RequirePasswordReEntry = 77               #: The user cannot complete the action until they re-enter their password
    ValueOutOfRange = 78                      #: the value entered is outside the acceptable range
    UnexpectedError = 79                      #: something happened that we didn't expect to ever happen
    Disabled = 80                             #: The requested service has been configured to be unavailable
    InvalidCEGSubmission = 81                 #: The set of files submitted to the CEG server are not valid !
    RestrictedDevice = 82                     #: The device being used is not allowed to perform this action
    RegionLocked = 83                         #: The action could not be complete because it is region restricted
    RateLimitExceeded = 84                    #: Temporary rate limit exceeded, try again later, different from k_EResultLimitExceeded which may be permanent
    AccountLoginDeniedNeedTwoFactor = 85      #: Need two-factor code to login
    ItemDeleted = 86                          #: The thing we're trying to access has been deleted
    AccountLoginDeniedThrottle = 87           #: login attempt failed, try to throttle response to possible attacker
    TwoFactorCodeMismatch = 88                #: two factor code mismatch
    TwoFactorActivationCodeMismatch = 89      #: activation code for two-factor didn't match
    AccountAssociatedToMultiplePartners = 90  #: account has been associated with multiple partners
    NotModified = 91                          #: data not modified
    NoMobileDevice = 92                       #: the account does not have a mobile device associated with it
    TimeNotSynced = 93                        #: the time presented is out of range or tolerance
    SMSCodeFailed = 94                        #: SMS code failure (no match, none pending, etc.)
    AccountLimitExceeded = 95                 #: Too many accounts access this resource
    AccountActivityLimitExceeded = 96         #: Too many changes to this account
    PhoneActivityLimitExceeded = 97           #: Too many changes to this phone
    RefundToWallet = 98                       #: Cannot refund to payment method, must use wallet
    EmailSendFailure = 99                     #: Cannot send an email
    NotSettled = 100                          #: Can't perform operation till payment has settled
    NeedCaptcha = 101                         #: Needs to provide a valid captcha
    GSLTDenied = 102                          #: a game server login token owned by this token's owner has been banned
    GSOwnerDenied = 103                       #: game server owner is denied for other reason (account lock, community ban, vac ban, missing phone)
    InvalidItemType = 104                     #: the type of thing we were requested to act on is invalid
    IPBanned = 105                            #: the ip address has been banned from taking this action
    GSLTExpired = 106                         #: this token has expired from disuse; can be reset for use
    InsufficientFunds = 107                   #: user doesn't have enough wallet funds to complete the action
    TooManyPending = 108                      #: There are too many of this thing pending already
    NoSiteLicensesFound = 109                 #: No site licenses found
    WGNetworkSendExceeded = 110               #: the WG couldn't send a response because we exceeded max network send size


class EUniverse(SteamIntEnum):
    Invalid = 0
    Public = 1
    Beta = 2
    Internal = 3
    Dev = 4
#   RC = 5  #: doesn't exit anymore
    Max = 6


class EType(SteamIntEnum):
    Invalid = 0
    Individual = 1      #: single user account
    Multiseat = 2       #: multiseat (e.g. cybercafe) account
    GameServer = 3      #: game server account
    AnonGameServer = 4  #: anonymous game server account
    Pending = 5         #: pending
    ContentServer = 6   #: content server
    Clan = 7
    Chat = 8
    ConsoleUser = 9     #: Fake SteamID for local PSN account on PS3 or Live account on 360, etc.
    AnonUser = 10
    Max = 11


class EInstanceFlag(SteamIntEnum):
    MMSLobby = 0x20000
    Lobby = 0x40000
    Clan = 0x80000


class EVanityUrlType(SteamIntEnum):
    Individual = 1
    Group = 2
    GameGroup = 3


class EServerType(SteamIntEnum):
    Invalid = -1
    First = 0
    GM = 1
    BUM = 2  # obsolete
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
    SLC = 20
    UFS = 21
    Util = 23
    DSS = 24
    Community = 24
    P2PRelayOBSOLETE = 25
    AppInformation = 26
    Spare = 27
    FTS = 28
    EPM = 29  # obsolete
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
#   Store = 51 # obsolete
    StoreFeature = 51
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
    TaxForm = 67
    ExternalMonitor = 68
    Parental = 69
    PartnerUpload = 70
    Partner = 71
    ES = 72
    DepotWebContent = 73
    ExternalConfig = 74
    GameNotifications = 75
    MarketRepl = 76
    MarketSearch = 77
    Localization = 78
    Steam2Emulator = 79
    PublicTest = 80
    SolrMgr = 81
    BroadcastRelay = 82
    BroadcastDirectory = 83
    VideoManager = 84
    TradeOffer = 85
    BroadcastChat = 86
    Phone = 87
    AccountScore = 88
    Support = 89
    LogRequest = 90
    LogWorker = 91
    EmailDelivery = 92
    InventoryManagement = 93
    Auth = 94
    StoreCatalog = 95
    HLTVRelay = 96

    Max = 97


class EOSType(SteamIntEnum):
    Unknown = -1

    IOSUnknown = -600

    AndroidUnknown = -500

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
    MacOS1011 = -86
    MacOS1012 = -85
    MacOSMax = -1

    LinuxUnknown = -203
    Linux22 = -202
    Linux24 = -201
    Linux26 = -200
    Linux32 = -199
    Linux35 = -198
    Linux36 = -197
    Linux310 = -196
    LinuxMax = -103

    WinUnknown = 0
    Win311 = 1
    Win95 = 2
    Win98 = 3
    WinME = 4
    WinNT = 5
#   Win200 = 6 # obsolete
    Win2000 = 6
    WinXP = 7
    Win2003 = 8
    WinVista = 9
#   Win7 = 10 # obsolete
    Windows7 = 10
    Win2008 = 11
    Win2012 = 12
#   Win8 = 13 # obsolete "renamed to Windows8"
    Windows8 = 13
#   Win81 = 14 # obsolete "renamed to Windows81"
    Windows81 = 14
    Win2012R2 = 15
#   Win10 = 16 # obsolete "renamed to Windows10"
    Windows10 = 16

    WinMAX = 15

    Max = 26


class EFriendRelationship(SteamIntEnum):
    NONE = 0
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
    ParentalSettings = 268435456
    ThirdPartySupport = 536870912
    NeedsSSANextSteamLogon = 1073741824


class EFriendFlags(SteamIntEnum):
    NONE = 0
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
    ChatMember = 4096
    FlagAll = 65535


class EPersonaState(SteamIntEnum):
    Offline = 0
    Online = 1
    Busy = 2
    Away = 3
    Snooze = 4
    LookingToTrade = 5
    LookingToPlay = 6
    Max = 7


class EPersonaStateFlag(SteamIntEnum):
    HasRichPresence = 1
    InJoinableGame = 2
    HasGoldenProfile = 4
#   OnlineUsingWeb = 256 obsolete "renamed to ClientTypeWeb"
    ClientTypeWeb = 256
#   OnlineUsingMobile = 512 obsolete "renamed to ClientTypeMobile"
    ClientTypeMobile = 512
#   OnlineUsingBigPicture = 1024 obsolete "renamed to ClientTypeTenfoot"
    ClientTypeTenfoot = 1024
#   OnlineUsingVR = 2048 obsolete "renamed to ClientTypeVR"
    ClientTypeVR = 2048
    LaunchTypeGamepad = 4096


class EClientPersonaStateFlag(SteamIntEnum):
    Status = 1
    PlayerName = 2
    QueryPort = 4
    SourceID = 8
    Presence = 16
    Metadata = 32  # obsolete
    LastSeen = 64
    ClanInfo = 128
    GameExtraInfo = 256
    GameDataBlob = 512
    ClanTag = 1024
    Facebook = 2048


class ELeaderboardDataRequest(SteamIntEnum):
    Global = 0
    GlobalAroundUser = 1
    Friends = 2
    Users = 3


class ELeaderboardSortMethod(SteamIntEnum):
    NONE = 0
    Ascending = 1
    Descending = 2


class ELeaderboardDisplayType(SteamIntEnum):
    NONE = 0
    Numeric = 1
    TimeSeconds = 2
    TimeMilliSeconds = 3


class ELeaderboardUploadScoreMethod(SteamIntEnum):
    NONE = 0
    KeepBest = 1
    ForceUpdate = 2


class ETwoFactorTokenType(SteamIntEnum):
    NONE = 0
    ValveMobileApp = 1
    ThirdParty = 2


class EChatEntryType(SteamIntEnum):
    Invalid = 0
    ChatMsg = 1             #: Normal text message from another user
    Typing = 2              #: Another user is typing (not used in multi-user chat)
    InviteGame = 3          #: Invite from other user into that users current game
    Emote = 4               #: text emote message (deprecated, should be treated as ChatMsg)
    LobbyGameStart = 5      #: lobby game is starting (dead - listen for LobbyGameCreated_t callback instead)
    LeftConversation = 6    #: user has left the conversation ( closed chat window )
    Entered = 7             #: user has entered the conversation (used in multi-user chat and group chat)
    WasKicked = 8           #: user was kicked (data: 64-bit steamid of actor performing the kick)
    WasBanned = 9           #: user was banned (data: 64-bit steamid of actor performing the ban)
    Disconnected = 10       #: user disconnected
    HistoricalChat = 11     #: a chat message from user's chat history or offilne message
    Reserved1 = 12          #: No longer used
    Reserved2 = 13          #: No longer used
    LinkBlocked = 14        #: a link was removed by the chat filter.


class EChatRoomEnterResponse(SteamIntEnum):
    Success = 1              #: Success
    DoesntExist = 2          #: Chat doesn't exist (probably closed)
    NotAllowed = 3           #: General Denied - You don't have the permissions needed to join the chat
    Full = 4                 #: Chat room has reached its maximum size
    Error = 5                #: Unexpected Error
    Banned = 6               #: You are banned from this chat room and may not join
    Limited = 7              #: Joining this chat is not allowed because you are a limited user (no value on account)
    ClanDisabled = 8         #: Attempt to join a clan chat when the clan is locked or disabled
    CommunityBan = 9         #: Attempt to join a chat when the user has a community lock on their account
    MemberBlockedYou = 10    #: Join failed - some member in the chat has blocked you from joining
    YouBlockedMember = 11    #: Join failed - you have blocked some member already in the chat
    NoRankingDataLobby = 12  #: No longer used
    NoRankingDataUser = 13   #: No longer used
    RankOutOfRange = 14      #: No longer used
    RatelimitExceeded = 15   #: Join failed - to many join attempts in a very short period of time


class ECurrencyCode(SteamIntEnum):
    Invalid = 0
    USD = 1
    GBP = 2
    EUR = 3
    CHF = 4
    RUB = 5
    PLN = 6
    BRL = 7
    JPY = 8
    NOK = 9
    IDR = 10
    MYR = 11
    PHP = 12
    SGD = 13
    THB = 14
    VND = 15
    KRW = 16
    TRY = 17
    UAH = 18
    MXN = 19
    CAD = 20
    AUD = 21
    NZD = 22
    CNY = 23
    INR = 24
    CLP = 25
    PEN = 26
    COP = 27
    ZAR = 28
    HKD = 29
    TWD = 30
    SAR = 31
    AED = 32
    SEK = 33
    ARS = 34
    ILS = 35
    BYN = 36
    KZT = 37
    KWD = 38
    QAR = 39
    CRC = 40
    UYU = 41
    Max = 42


class EDepotFileFlag(SteamIntEnum):
    UserConfig = 1
    VersionedUserConfig = 2
    Encrypted = 4
    ReadOnly = 8
    Hidden = 16
    Executable = 32
    Directory = 64
    CustomExecutable = 128
    InstallScript = 256
    Symlink = 512


# Do not remove
from enum import EnumMeta

__all__ = [obj.__name__
           for obj in globals().values()
           if obj.__class__ is EnumMeta and obj.__name__ != 'SteamIntEnum'
           ]

del EnumMeta
