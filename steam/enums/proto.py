from steam.enums.base import SteamIntEnum

class E_STAR_GlyphWriteResult(SteamIntEnum):
    Success = 0
    InvalidMessage = 1
    InvalidJSON = 2
    SQLError = 3

class EACState(SteamIntEnum):
    Unknown = 0
    Disconnected = 1
    Connected = 2
    ConnectedSlow = 3

class EAgreementType(SteamIntEnum):
    Invalid = -1
    GlobalSSA = 0
    ChinaSSA = 1

class EAudioFormat(SteamIntEnum):
    EAudioFormatNone = 0
    EAudioFormat16BitLittleEndian = 1
    EAudioFormatFloat = 2

EAuthSessionGuardType = SteamIntEnum('EAuthSessionGuardType', {
    'Unknown': 0,
    'None': 1,
    'EmailCode': 2,
    'DeviceCode': 3,
    'DeviceConfirmation': 4,
    'EmailConfirmation': 5,
    'MachineToken': 6,
    })

class EAuthSessionSecurityHistory(SteamIntEnum):
    Invalid = 0
    UsedPreviously = 1
    NoPriorHistory = 2

class EAuthTokenPlatformType(SteamIntEnum):
    Unknown = 0
    SteamClient = 1
    WebBrowser = 2
    MobileApp = 3

class EAuthTokenRevokeAction(SteamIntEnum):
    EAuthTokenRevokeLogout = 0
    EAuthTokenRevokePermanent = 1
    EAuthTokenRevokeReplaced = 2
    EAuthTokenRevokeSupport = 3

class EAuthTokenState(SteamIntEnum):
    Invalid = 0
    New = 1
    Confirmed = 2
    Issued = 3
    Denied = 4
    LoggedOut = 5
    Revoked = 99

class EBatteryState(SteamIntEnum):
    Unknown = 0
    Discharging = 1
    Charging = 2
    Full = 3

class EBluetoothDeviceType(SteamIntEnum):
    BluetoothDeviceType_Invalid = 0
    BluetoothDeviceType_Unknown = 1
    BluetoothDeviceType_Phone = 2
    BluetoothDeviceType_Computer = 3
    BluetoothDeviceType_Headset = 4
    BluetoothDeviceType_Headphones = 5
    BluetoothDeviceType_Speakers = 6
    BluetoothDeviceType_OtherAudio = 7
    BluetoothDeviceType_Mouse = 8
    BluetoothDeviceType_Joystick = 9
    BluetoothDeviceType_Gamepad = 10
    BluetoothDeviceType_Keyboard = 11

class EBroadcastChatPermission(SteamIntEnum):
    EBroadcastChatPermissionPublic = 0
    EBroadcastChatPermissionOwnsApp = 1

EBroadcastImageType = SteamIntEnum('EBroadcastImageType', {
    'None': 0,
    'Offline': 1,
    'Standby': 2,
    'Avatar': 3,
    'Summary': 4,
    'Background': 5,
    'Emoticon': 6,
    })

class EBroadcastWatchLocation(SteamIntEnum):
    Invalid = 0
    SteamTV_Tab = 1
    SteamTV_WatchParty = 2
    Chat_Tab = 3
    Chat_WatchParty = 4
    CommunityPage = 5
    StoreAppPage = 6
    InGame = 7
    BigPicture = 8
    SalesPage = 9
    CuratorPage = 10
    DeveloperPage = 11
    Chat_Friends = 12
    SteamTV_Web = 13

class EChatRoomGroupRank(SteamIntEnum):
    Default = 0
    Viewer = 10
    Guest = 15
    Member = 20
    Moderator = 30
    Officer = 40
    Owner = 50
    TestInvalid = 99

EChatRoomJoinState = SteamIntEnum('EChatRoomJoinState', {
    'Default': 0,
    'None': 1,
    'Joined': 2,
    'TestInvalid': 99,
    })

class EChatRoomMemberStateChange(SteamIntEnum):
    Invalid = 0
    Joined = 1
    Parted = 2
    Kicked = 3
    Invited = 4
    RankChanged = 7
    InviteDismissed = 8
    Muted = 9
    Banned = 10
    RolesChanged = 12

class EChatRoomMessageReactionType(SteamIntEnum):
    Invalid = 0
    Emoticon = 1
    Sticker = 2

class EChatRoomNotificationLevel(SteamIntEnum):
    EChatroomNotificationLevel_Invalid = 0
    EChatroomNotificationLevel_None = 1
    EChatroomNotificationLevel_MentionMe = 2
    EChatroomNotificationLevel_MentionAll = 3
    EChatroomNotificationLevel_AllMessages = 4

class EChatRoomServerMessage(SteamIntEnum):
    EChatRoomServerMsg_Invalid = 0
    EChatRoomServerMsg_RenameChatRoom = 1
    EChatRoomServerMsg_Joined = 2
    EChatRoomServerMsg_Parted = 3
    EChatRoomServerMsg_Kicked = 4
    EChatRoomServerMsg_Invited = 5
    EChatRoomServerMsg_InviteDismissed = 8
    EChatRoomServerMsg_ChatRoomTaglineChanged = 9
    EChatRoomServerMsg_ChatRoomAvatarChanged = 10
    EChatRoomServerMsg_AppCustom = 11

class ECloudStoragePersistState(SteamIntEnum):
    ECloudStoragePersistStatePersisted = 0
    ECloudStoragePersistStateForgotten = 1
    ECloudStoragePersistStateDeleted = 2

class EColorProfile(SteamIntEnum):
    Invalid = 0
    Native = 1
    Standard = 2
    Vivid = 3

class ECommunityItemClass(SteamIntEnum):
    Invalid = 0
    Badge = 1
    GameCard = 2
    ProfileBackground = 3
    Emoticon = 4
    BoosterPack = 5
    Consumable = 6
    GameGoo = 7
    ProfileModifier = 8
    Scene = 9
    SalienItem = 10
    Sticker = 11
    ChatEffect = 12
    MiniProfileBackground = 13
    AvatarFrame = 14
    AnimatedAvatar = 15
    SteamDeckKeyboardSkin = 16

class EContentCheckProvider(SteamIntEnum):
    Invalid = 0
    Google = 1
    Amazon = 2
    Local = 3

class ECPUGovernor(SteamIntEnum):
    Invalid = 0
    Perf = 1
    Powersave = 2
    Manual = 3

class EExternalAccountType(SteamIntEnum):
    EExternalNone = 0
    EExternalSteamAccount = 1
    EExternalGoogleAccount = 2
    EExternalFacebookAccount = 3
    EExternalTwitterAccount = 4
    EExternalTwitchAccount = 5
    EExternalYouTubeChannelAccount = 6
    EExternalFacebookPage = 7

class EFrameAccumulatedStat(SteamIntEnum):
    EFrameStatFPS = 0
    EFrameStatCaptureDurationMS = 1
    EFrameStatConvertDurationMS = 2
    EFrameStatEncodeDurationMS = 3
    EFrameStatSteamDurationMS = 4
    EFrameStatServerDurationMS = 5
    EFrameStatNetworkDurationMS = 6
    EFrameStatDecodeDurationMS = 7
    EFrameStatDisplayDurationMS = 8
    EFrameStatClientDurationMS = 9
    EFrameStatFrameDurationMS = 10
    EFrameStatInputLatencyMS = 11
    EFrameStatGameLatencyMS = 12
    EFrameStatRoundTripLatencyMS = 13
    EFrameStatPingTimeMS = 14
    EFrameStatServerBitrateKbitPerSec = 15
    EFrameStatClientBitrateKbitPerSec = 16
    EFrameStatLinkBandwidthKbitPerSec = 17
    EFrameStatPacketLossPercentage = 18

EGameSearchAction = SteamIntEnum('EGameSearchAction', {
    'None': 0,
    'Accept': 1,
    'Decline': 2,
    'Cancel': 3,
    })

class EGameSearchResult(SteamIntEnum):
    Invalid = 0
    SearchInProgress = 1
    SearchFailedNoHosts = 2
    SearchGameFound = 3
    SearchCompleteAccepted = 4
    SearchCompleteDeclined = 5
    SearchCanceled = 6

class EGetChannelsAlgorithm(SteamIntEnum):
    Default = 1
    Friends = 2
    Featured = 3
    Developer = 4
    Following = 5

class EGetGamesAlgorithm(SteamIntEnum):
    Default = 1
    MostPlayed = 2
    PopularNew = 3

class EGPUPerformanceLevel(SteamIntEnum):
    Invalid = 0
    Auto = 1
    Manual = 2
    Low = 3
    High = 4
    Profiling = 5

class EGraphicsPerfOverlayLevel(SteamIntEnum):
    Hidden = 0
    Basic = 1
    Medium = 2
    Full = 3
    Minimal = 4

class EInternalAccountType(SteamIntEnum):
    EInternalSteamAccountType = 1
    EInternalClanType = 2
    EInternalAppType = 3
    EInternalBroadcastChannelType = 4

class EKeyEscrowUsage(SteamIntEnum):
    EKeyEscrowUsageStreamingDevice = 0

class ELobbyStatus(SteamIntEnum):
    ELobbyStatusInvalid = 0
    ELobbyStatusExists = 1
    ELobbyStatusDoesNotExist = 2
    ELobbyStatusNotAMember = 3

class ELogFileType(SteamIntEnum):
    ELogFileSystemBoot = 0
    ELogFileSystemReset = 1
    ELogFileSystemDebug = 2

class EMarketingMessageAssociationType(SteamIntEnum):
    EMarketingMessageNoAssociation = 0
    EMarketingMessageAppAssociation = 1
    EMarketingMessageSubscriptionAssociation = 2
    EMarketingMessagePublisherAssociation = 3
    EMarketingMessageGenreAssociation = 4
    EMarketingMessageBundleAssociation = 5

class EMarketingMessageLookupType(SteamIntEnum):
    EMarketingMessageLookupInvalid = 0
    EMarketingMessageLookupByGID = 1
    EMarketingMessageLookupActive = 2
    EMarketingMessageLookupByTitleWithType = 3
    EMarketingMessageLookupByGIDList = 4

class EMarketingMessageType(SteamIntEnum):
    EMarketingMessageInvalid = 0
    EMarketingMessageNowAvailable = 1
    EMarketingMessageWeekendDeal = 2
    EMarketingMessagePrePurchase = 3
    EMarketingMessagePlayNow = 4
    EMarketingMessagePreloadNow = 5
    EMarketingMessageGeneral = 6
    EMarketingMessageDemoQuit = 7
    EMarketingMessageGifting = 8
    EMarketingMessageEJsKorner = 9

class EMarketingMessageVisibility(SteamIntEnum):
    EMarketingMessageVisibleBeta = 1
    EMarketingMessageVisiblePublic = 2

class EMessageReactionType(SteamIntEnum):
    Invalid = 0
    Emoticon = 1
    Sticker = 2

class ENotificationSetting(SteamIntEnum):
    ENotificationSettingNotifyUseDefault = 0
    ENotificationSettingAlways = 1
    ENotificationSettingNever = 2

class EOSBranch(SteamIntEnum):
    Unknown = 0
    Release = 1
    ReleaseCandidate = 2
    Beta = 3
    BetaCandidate = 4
    Main = 5

class EPlaytestStatus(SteamIntEnum):
    ETesterStatusNone = 0
    ETesterStatusPending = 1
    ETesterStatusInvited = 2
    ETesterStatusGranted = 3

class EProfileCustomizationStyle(SteamIntEnum):
    EProfileCustomizationStyleDefault = 0
    EProfileCustomizationStyleSelected = 1
    EProfileCustomizationStyleRarest = 2
    EProfileCustomizationStyleMostRecent = 3
    EProfileCustomizationStyleRandom = 4
    EProfileCustomizationStyleHighestRated = 5

class EProfileCustomizationType(SteamIntEnum):
    EProfileCustomizationTypeInvalid = 0
    EProfileCustomizationTypeRareAchievementShowcase = 1
    EProfileCustomizationTypeGameCollector = 2
    EProfileCustomizationTypeItemShowcase = 3
    EProfileCustomizationTypeTradeShowcase = 4
    EProfileCustomizationTypeBadges = 5
    EProfileCustomizationTypeFavoriteGame = 6
    EProfileCustomizationTypeScreenshotShowcase = 7
    EProfileCustomizationTypeCustomText = 8
    EProfileCustomizationTypeFavoriteGroup = 9
    EProfileCustomizationTypeRecommendation = 10
    EProfileCustomizationTypeWorkshopItem = 11
    EProfileCustomizationTypeMyWorkshop = 12
    EProfileCustomizationTypeArtworkShowcase = 13
    EProfileCustomizationTypeVideoShowcase = 14
    EProfileCustomizationTypeGuides = 15
    EProfileCustomizationTypeMyGuides = 16
    EProfileCustomizationTypeAchievements = 17
    EProfileCustomizationTypeGreenlight = 18
    EProfileCustomizationTypeMyGreenlight = 19
    EProfileCustomizationTypeSalien = 20
    EProfileCustomizationTypeLoyaltyRewardReactions = 21
    EProfileCustomizationTypeSingleArtworkShowcase = 22
    EProfileCustomizationTypeAchievementsCompletionist = 23

class EProtoExecutionSite(SteamIntEnum):
    EProtoExecutionSiteUnknown = 0
    EProtoExecutionSiteSteamClient = 2

class EProvideDeckFeedbackPreference(SteamIntEnum):
    Unset = 0
    Yes = 1
    No = 2

class EPublishedFileForSaleStatus(SteamIntEnum):
    PFFSS_NotForSale = 0
    PFFSS_PendingApproval = 1
    PFFSS_ApprovedForSale = 2
    PFFSS_RejectedForSale = 3
    PFFSS_NoLongerForSale = 4
    PFFSS_TentativeApproval = 5

class EPublishedFileRevision(SteamIntEnum):
    Default = 0
    Latest = 1
    ApprovedSnapshot = 2
    ApprovedSnapshot_China = 3
    RejectedSnapshot = 4
    RejectedSnapshot_China = 5

class EPublishedFileStorageSystem(SteamIntEnum):
    EPublishedFileStorageSystemInvalid = 0
    EPublishedFileStorageSystemLegacyCloud = 1
    EPublishedFileStorageSystemDepot = 2
    EPublishedFileStorageSystemUGCCloud = 3

class EScalingFilter(SteamIntEnum):
    Invalid = 0
    FSR = 1
    Nearest = 2
    Integer = 3
    Linear = 4
    NIS = 5

class ESDCardFormatStage(SteamIntEnum):
    Invalid = 0
    Starting = 1
    Testing = 2
    Rescuing = 3
    Formatting = 4
    Finalizing = 5

class ESessionPersistence(SteamIntEnum):
    Invalid = -1
    Ephemeral = 0
    Persistent = 1

class ESteamDeckCompatibilityCategory(SteamIntEnum):
    Unknown = 0
    Unsupported = 1
    Playable = 2
    Verified = 3

class ESteamDeckCompatibilityFeedback(SteamIntEnum):
    Unset = 0
    Agree = 1
    Disagree = 2
    Ignore = 3

class ESteamDeckCompatibilityResultDisplayType(SteamIntEnum):
    Invisible = 0
    Informational = 1
    Unsupported = 2
    Playable = 3
    Verified = 4

class ESteamTVContentTemplate(SteamIntEnum):
    Invalid = 0
    Takeover = 1
    SingleGame = 2
    GameList = 3
    QuickExplore = 4
    ConveyorBelt = 5
    WatchParty = 6
    Developer = 7
    Event = 8

class EStorageBlockContentType(SteamIntEnum):
    Invalid = 0
    Unknown = 1
    FileSystem = 2
    Crypto = 3
    Raid = 4

class EStorageBlockFileSystemType(SteamIntEnum):
    Invalid = 0
    Unknown = 1
    VFat = 2
    Ext4 = 3

class EStoreAppType(SteamIntEnum):
    Game = 0
    Demo = 1
    Mod = 2
    Movie = 3
    DLC = 4
    Guide = 5
    Software = 6
    Video = 7
    Series = 8
    Episode = 9
    Hardware = 10
    Music = 11
    Beta = 12
    Tool = 13
    Advertising = 14

class EStoreCategoryType(SteamIntEnum):
    Category = 0
    SupportedPlayers = 1
    Feature = 2
    ControllerSupport = 3
    CloudGaming = 4
    MAX = 5

class EStoreDiscoveryQueueType(SteamIntEnum):
    EStoreDiscoveryQueueTypeNew = 0
    EStoreDiscoveryQueueTypeComingSoon = 1
    EStoreDiscoveryQueueTypeRecommended = 2
    EStoreDiscoveryQueueTypeEveryNewRelease = 3
    EStoreDiscoveryQueueTypeMLRecommender = 5
    EStoreDiscoveryQueueTypeWishlistOnSale = 6
    EStoreDiscoveryQueueTypeDLC = 7
    EStoreDiscoveryQueueTypeDLCOnSale = 8
    EStoreDiscoveryQueueTypeRecommendedComingSoon = 9
    EStoreDiscoveryQueueTypeRecommendedFree = 10
    EStoreDiscoveryQueueTypeRecommendedOnSale = 11
    EStoreDiscoveryQueueTypeRecommendedDemos = 12
    EStoreDiscoveryQueueTypeDLCNewReleases = 13
    EStoreDiscoveryQueueTypeDLCTopSellers = 14
    EStoreDiscoveryQueueTypeMAX = 15

class EStoreItemType(SteamIntEnum):
    Invalid = -1
    App = 0
    Package = 1
    Bundle = 2
    Mtx = 3

class EStreamActivity(SteamIntEnum):
    EStreamActivityIdle = 1
    EStreamActivityGame = 2
    EStreamActivityDesktop = 3
    EStreamActivitySecureDesktop = 4
    EStreamActivityMusic = 5

class EStreamAudioCodec(SteamIntEnum):
    EStreamAudioCodecNone = 0
    EStreamAudioCodecRaw = 1
    EStreamAudioCodecVorbis = 2
    EStreamAudioCodecOpus = 3
    EStreamAudioCodecMP3 = 4
    EStreamAudioCodecAAC = 5

class EStreamBitrate(SteamIntEnum):
    EStreamBitrateAutodetect = -1
    EStreamBitrateUnlimited = 0

class EStreamChannel(SteamIntEnum):
    EStreamChannelInvalid = -1
    EStreamChannelDiscovery = 0
    EStreamChannelControl = 1
    EStreamChannelStats = 2
    EStreamChannelDataChannelStart = 3

class EStreamColorspace(SteamIntEnum):
    Unknown = 0
    BT601 = 1
    BT601_Full = 2
    BT709 = 3
    BT709_Full = 4

class EStreamControllerConfigMsg(SteamIntEnum):
    RequestConfigsForApp = 0
    ConfigResponse = 1
    PersonalizationResponse = 2
    ActiveConfigChange = 3
    RequestActiveConfig = 4

class EStreamControlMessage(SteamIntEnum):
    EStreamControlAuthenticationRequest = 1
    EStreamControlAuthenticationResponse = 2
    EStreamControlNegotiationInit = 3
    EStreamControlNegotiationSetConfig = 4
    EStreamControlNegotiationComplete = 5
    EStreamControlClientHandshake = 6
    EStreamControlServerHandshake = 7
    EStreamControlStartNetworkTest = 8
    EStreamControlKeepAlive = 9
    EStreamControl_LAST_SETUP_MESSAGE = 15
    EStreamControlStartAudioData = 50
    EStreamControlStopAudioData = 51
    EStreamControlStartVideoData = 52
    EStreamControlStopVideoData = 53
    EStreamControlInputMouseMotion = 54
    EStreamControlInputMouseWheel = 55
    EStreamControlInputMouseDown = 56
    EStreamControlInputMouseUp = 57
    EStreamControlInputKeyDown = 58
    EStreamControlInputKeyUp = 59
    EStreamControlInputGamepadAttached_OBSOLETE = 60
    EStreamControlInputGamepadEvent_OBSOLETE = 61
    EStreamControlInputGamepadDetached_OBSOLETE = 62
    EStreamControlShowCursor = 63
    EStreamControlHideCursor = 64
    EStreamControlSetCursor = 65
    EStreamControlGetCursorImage = 66
    EStreamControlSetCursorImage = 67
    EStreamControlDeleteCursor = 68
    EStreamControlSetTargetFramerate = 69
    EStreamControlInputLatencyTest = 70
    EStreamControlGamepadRumble_OBSOLETE = 71
    EStreamControlOverlayEnabled = 74
    EStreamControlInputControllerAttached_OBSOLETE = 75
    EStreamControlInputControllerState_OBSOLETE = 76
    EStreamControlTriggerHapticPulse_OBSOLETE = 77
    EStreamControlInputControllerDetached_OBSOLETE = 78
    EStreamControlVideoDecoderInfo = 80
    EStreamControlSetTitle = 81
    EStreamControlSetIcon = 82
    EStreamControlQuitRequest = 83
    EStreamControlSetQoS = 87
    EStreamControlInputControllerWirelessPresence_OBSOLETE = 88
    EStreamControlSetGammaRamp = 89
    EStreamControlVideoEncoderInfo = 90
    EStreamControlInputControllerStateHID_OBSOLETE = 93
    EStreamControlSetTargetBitrate = 94
    EStreamControlSetControllerPairingEnabled_OBSOLETE = 95
    EStreamControlSetControllerPairingResult_OBSOLETE = 96
    EStreamControlTriggerControllerDisconnect_OBSOLETE = 97
    EStreamControlSetActivity = 98
    EStreamControlSetStreamingClientConfig = 99
    EStreamControlSystemSuspend = 100
    EStreamControlSetControllerSettings_OBSOLETE = 101
    EStreamControlVirtualHereRequest = 102
    EStreamControlVirtualHereReady = 103
    EStreamControlVirtualHereShareDevice = 104
    EStreamControlSetSpectatorMode = 105
    EStreamControlRemoteHID = 106
    EStreamControlStartMicrophoneData = 107
    EStreamControlStopMicrophoneData = 108
    EStreamControlInputText = 109
    EStreamControlTouchConfigActive = 110
    EStreamControlGetTouchConfigData = 111
    EStreamControlSetTouchConfigData = 112
    EStreamControlSaveTouchConfigLayout = 113
    EStreamControlTouchActionSetActive = 114
    EStreamControlGetTouchIconData = 115
    EStreamControlSetTouchIconData = 116
    EStreamControlInputTouchFingerDown = 117
    EStreamControlInputTouchFingerMotion = 118
    EStreamControlInputTouchFingerUp = 119
    EStreamControlSetCaptureSize = 120
    EStreamControlSetFlashState = 121
    EStreamControlPause = 122
    EStreamControlResume = 123
    EStreamControlEnableHighResCapture = 124
    EStreamControlDisableHighResCapture = 125
    EStreamControlToggleMagnification = 126
    EStreamControlSetCapslock = 127
    EStreamControlSetKeymap = 128
    EStreamControlStopRequest = 129
    EStreamControlTouchActionSetLayerAdded = 130
    EStreamControlTouchActionSetLayerRemoved = 131
    EStreamControlRemotePlayTogetherGroupUpdate = 132
    EStreamControlSetInputTemporarilyDisabled = 133
    EStreamControlSetQualityOverride = 134
    EStreamControlSetBitrateOverride = 135
    EStreamControlShowOnScreenKeyboard = 136
    EStreamControlControllerConfigMsg = 137

class EStreamDataMessage(SteamIntEnum):
    EStreamDataPacket = 1
    EStreamDataLost = 2

class EStreamDiscoveryMessage(SteamIntEnum):
    EStreamDiscoveryPingRequest = 1
    EStreamDiscoveryPingResponse = 2

class EStreamFrameEvent(SteamIntEnum):
    EStreamInputEventStart = 0
    EStreamInputEventSend = 1
    EStreamInputEventRecv = 2
    EStreamInputEventQueued = 3
    EStreamInputEventHandled = 4
    EStreamFrameEventStart = 5
    EStreamFrameEventCaptureBegin = 6
    EStreamFrameEventCaptureEnd = 7
    EStreamFrameEventConvertBegin = 8
    EStreamFrameEventConvertEnd = 9
    EStreamFrameEventEncodeBegin = 10
    EStreamFrameEventEncodeEnd = 11
    EStreamFrameEventSend = 12
    EStreamFrameEventRecv = 13
    EStreamFrameEventDecodeBegin = 14
    EStreamFrameEventDecodeEnd = 15
    EStreamFrameEventUploadBegin = 16
    EStreamFrameEventUploadEnd = 17
    EStreamFrameEventComplete = 18

class EStreamFramerateLimiter(SteamIntEnum):
    EStreamFramerateSlowCapture = 1
    EStreamFramerateSlowConvert = 2
    EStreamFramerateSlowEncode = 4
    EStreamFramerateSlowNetwork = 8
    EStreamFramerateSlowDecode = 16
    EStreamFramerateSlowGame = 32
    EStreamFramerateSlowDisplay = 64

class EStreamFrameResult(SteamIntEnum):
    EStreamFrameResultPending = 0
    EStreamFrameResultDisplayed = 1
    EStreamFrameResultDroppedNetworkSlow = 2
    EStreamFrameResultDroppedNetworkLost = 3
    EStreamFrameResultDroppedDecodeSlow = 4
    EStreamFrameResultDroppedDecodeCorrupt = 5
    EStreamFrameResultDroppedLate = 6
    EStreamFrameResultDroppedReset = 7

class EStreamHostPlayAudioPreference(SteamIntEnum):
    EStreamHostPlayAudioDefault = 0
    EStreamHostPlayAudioAlways = 1

class EStreamingDataType(SteamIntEnum):
    EStreamingAudioData = 0
    EStreamingVideoData = 1
    EStreamingMicrophoneData = 2

class EStreamMouseButton(SteamIntEnum):
    EStreamMouseButtonLeft = 1
    EStreamMouseButtonRight = 2
    EStreamMouseButtonMiddle = 16
    EStreamMouseButtonX1 = 32
    EStreamMouseButtonX2 = 64
    EStreamMouseButtonUnknown = 4096

class EStreamMouseWheelDirection(SteamIntEnum):
    EStreamMouseWheelUp = 120
    EStreamMouseWheelDown = -120
    EStreamMouseWheelLeft = 3
    EStreamMouseWheelRight = 4

class EStreamP2PScope(SteamIntEnum):
    EStreamP2PScopeAutomatic = 0
    EStreamP2PScopeDisabled = 1
    EStreamP2PScopeOnlyMe = 2
    EStreamP2PScopeFriends = 3
    EStreamP2PScopeEveryone = 4

class EStreamQualityPreference(SteamIntEnum):
    EStreamQualityAutomatic = -1
    EStreamQualityFast = 1
    EStreamQualityBalanced = 2
    EStreamQualityBeautiful = 3

class EStreamStatsMessage(SteamIntEnum):
    EStreamStatsFrameEvents = 1
    EStreamStatsDebugDump = 2
    EStreamStatsLogMessage = 3
    EStreamStatsLogUploadBegin = 4
    EStreamStatsLogUploadData = 5
    EStreamStatsLogUploadComplete = 6

class EStreamVersion(SteamIntEnum):
    EStreamVersionNone = 0
    EStreamVersionCurrent = 1

class EStreamVideoCodec(SteamIntEnum):
    EStreamVideoCodecNone = 0
    EStreamVideoCodecRaw = 1
    EStreamVideoCodecVP8 = 2
    EStreamVideoCodecVP9 = 3
    EStreamVideoCodecH264 = 4
    EStreamVideoCodecHEVC = 5
    EStreamVideoCodecORBX1 = 6
    EStreamVideoCodecORBX2 = 7

class ESystemAudioChannel(SteamIntEnum):
    SystemAudioChannel_Invalid = 0
    SystemAudioChannel_Aggregated = 1
    SystemAudioChannel_FrontLeft = 2
    SystemAudioChannel_FrontRight = 3
    SystemAudioChannel_LFE = 4
    SystemAudioChannel_BackLeft = 5
    SystemAudioChannel_BackRight = 6
    SystemAudioChannel_FrontCenter = 7
    SystemAudioChannel_Unknown = 8
    SystemAudioChannel_Mono = 9

class ESystemAudioDirection(SteamIntEnum):
    SystemAudioDirection_Invalid = 0
    SystemAudioDirection_Input = 1
    SystemAudioDirection_Output = 2

class ESystemAudioPortDirection(SteamIntEnum):
    SystemAudioPortDirection_Invalid = 0
    SystemAudioPortDirection_Input = 1
    SystemAudioPortDirection_Output = 2

class ESystemAudioPortType(SteamIntEnum):
    SystemAudioPortType_Invalid = 0
    SystemAudioPortType_Unknown = 1
    SystemAudioPortType_Audio32f = 2
    SystemAudioPortType_Midi8b = 3
    SystemAudioPortType_Video32RGBA = 4

class ESystemFanControlMode(SteamIntEnum):
    SystemFanControlMode_Invalid = 0
    SystemFanControlMode_Disabled = 1
    SystemFanControlMode_Default = 2

class ESystemServiceState(SteamIntEnum):
    Unavailable = 0
    Disabled = 1
    Enabled = 2

class ETextFilterSetting(SteamIntEnum):
    ETextFilterSettingSteamLabOptedOut = 0
    ETextFilterSettingEnabled = 1
    ETextFilterSettingEnabledAllowProfanity = 2
    ETextFilterSettingDisabled = 3

class ETouchGesture(SteamIntEnum):
    ETouchGestureNone = 0
    ETouchGestureTouch = 1
    ETouchGestureTap = 2
    ETouchGestureDoubleTap = 3
    ETouchGestureShortPress = 4
    ETouchGestureLongPress = 5
    ETouchGestureLongTap = 6
    ETouchGestureTwoFingerTap = 7
    ETouchGestureTapCancelled = 8
    ETouchGesturePinchBegin = 9
    ETouchGesturePinchUpdate = 10
    ETouchGesturePinchEnd = 11
    ETouchGestureFlingStart = 12
    ETouchGestureFlingCancelled = 13

class EUpdaterState(SteamIntEnum):
    Invalid = 0
    UpToDate = 2
    Checking = 3
    Available = 4
    Applying = 5
    ClientRestartPending = 6
    SystemRestartPending = 7

class EUpdaterType(SteamIntEnum):
    Invalid = 0
    Client = 1
    OS = 2
    BIOS = 3
    Aggregated = 4
    Test1 = 5
    Test2 = 6
    Dummy = 7

EUserReviewScore = SteamIntEnum('EUserReviewScore', {
    'None': 0,
    'OverwhelminglyNegative': 1,
    'VeryNegative': 2,
    'Negative': 3,
    'MostlyNegative': 4,
    'Mixed': 5,
    'MostlyPositive': 6,
    'Positive': 7,
    'VeryPositive': 8,
    'OverwhelminglyPositive': 9,
    })

class EUserReviewScorePreference(SteamIntEnum):
    Unset = 0
    IncludeAll = 1
    ExcludeBombs = 2

class EVideoFormat(SteamIntEnum):
    EVideoFormatNone = 0
    EVideoFormatYV12 = 1
    EVideoFormatAccel = 2

__all__ = [
    'E_STAR_GlyphWriteResult',
    'EACState',
    'EAgreementType',
    'EAudioFormat',
    'EAuthSessionGuardType',
    'EAuthSessionSecurityHistory',
    'EAuthTokenPlatformType',
    'EAuthTokenRevokeAction',
    'EAuthTokenState',
    'EBatteryState',
    'EBluetoothDeviceType',
    'EBroadcastChatPermission',
    'EBroadcastImageType',
    'EBroadcastWatchLocation',
    'EChatRoomGroupRank',
    'EChatRoomJoinState',
    'EChatRoomMemberStateChange',
    'EChatRoomMessageReactionType',
    'EChatRoomNotificationLevel',
    'EChatRoomServerMessage',
    'ECloudStoragePersistState',
    'EColorProfile',
    'ECommunityItemClass',
    'EContentCheckProvider',
    'ECPUGovernor',
    'EExternalAccountType',
    'EFrameAccumulatedStat',
    'EGameSearchAction',
    'EGameSearchResult',
    'EGetChannelsAlgorithm',
    'EGetGamesAlgorithm',
    'EGPUPerformanceLevel',
    'EGraphicsPerfOverlayLevel',
    'EInternalAccountType',
    'EKeyEscrowUsage',
    'ELobbyStatus',
    'ELogFileType',
    'EMarketingMessageAssociationType',
    'EMarketingMessageLookupType',
    'EMarketingMessageType',
    'EMarketingMessageVisibility',
    'EMessageReactionType',
    'ENotificationSetting',
    'EOSBranch',
    'EPlaytestStatus',
    'EProfileCustomizationStyle',
    'EProfileCustomizationType',
    'EProtoExecutionSite',
    'EProvideDeckFeedbackPreference',
    'EPublishedFileForSaleStatus',
    'EPublishedFileRevision',
    'EPublishedFileStorageSystem',
    'EScalingFilter',
    'ESDCardFormatStage',
    'ESessionPersistence',
    'ESteamDeckCompatibilityCategory',
    'ESteamDeckCompatibilityFeedback',
    'ESteamDeckCompatibilityResultDisplayType',
    'ESteamTVContentTemplate',
    'EStorageBlockContentType',
    'EStorageBlockFileSystemType',
    'EStoreAppType',
    'EStoreCategoryType',
    'EStoreDiscoveryQueueType',
    'EStoreItemType',
    'EStreamActivity',
    'EStreamAudioCodec',
    'EStreamBitrate',
    'EStreamChannel',
    'EStreamColorspace',
    'EStreamControllerConfigMsg',
    'EStreamControlMessage',
    'EStreamDataMessage',
    'EStreamDiscoveryMessage',
    'EStreamFrameEvent',
    'EStreamFramerateLimiter',
    'EStreamFrameResult',
    'EStreamHostPlayAudioPreference',
    'EStreamingDataType',
    'EStreamMouseButton',
    'EStreamMouseWheelDirection',
    'EStreamP2PScope',
    'EStreamQualityPreference',
    'EStreamStatsMessage',
    'EStreamVersion',
    'EStreamVideoCodec',
    'ESystemAudioChannel',
    'ESystemAudioDirection',
    'ESystemAudioPortDirection',
    'ESystemAudioPortType',
    'ESystemFanControlMode',
    'ESystemServiceState',
    'ETextFilterSetting',
    'ETouchGesture',
    'EUpdaterState',
    'EUpdaterType',
    'EUserReviewScore',
    'EUserReviewScorePreference',
    'EVideoFormat',
    ]
