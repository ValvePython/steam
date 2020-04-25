"""Classes to (de)serialize various struct messages"""
import struct
import six
import vdf
from six.moves import range
from steam.enums import EResult, EUniverse
from steam.enums.emsg import EMsg
from steam.utils.binary import StructReader

_emsg_map = {}

def get_struct(emsg):
    return _emsg_map.get(emsg, None)

class StructMessageMeta(type):
    """Automatically adds subclasses of :class:`StructMessage` to the ``EMsg`` map"""

    def __new__(metacls, name, bases, classdict):
        cls = type.__new__(metacls, name, bases, classdict)

        if name != 'StructMessage':
            try:
                _emsg_map[EMsg[name]] = cls
            except KeyError:
                pass

        return cls

@six.add_metaclass(StructMessageMeta)
class StructMessage:
    def __init__(self, data=None):
        if data: self.load(data)

    def serialize(self):
        raise NotImplementedError

    def load(self, data):
        raise NotImplementedError


class ChannelEncryptRequest(StructMessage):
    protocolVersion = 1
    universe = EUniverse.Invalid
    challenge = b''

    def serialize(self):
        return struct.pack("<II", self.protocolVersion, self.universe) + self.challenge

    def load(self, data):
        (self.protocolVersion,
         universe,
         ) = struct.unpack_from("<II", data)

        self.universe = EUniverse(universe)

        if len(data) > 8:
            self.challenge = data[8:]

    def __str__(self):
        return '\n'.join(["protocolVersion: %s" % self.protocolVersion,
                          "universe: %s" % repr(self.universe),
                          "challenge: %s" % repr(self.challenge),
                          ])

class ChannelEncryptResponse(StructMessage):
    protocolVersion = 1
    keySize = 128
    key = ''
    crc = 0

    def serialize(self):
        return struct.pack("<II128sII",
                           self.protocolVersion,
                           self.keySize,
                           self.key,
                           self.crc,
                           0
                           )

    def load(self, data):
        (self.protocolVersion,
         self.keySize,
         self.key,
         self.crc,
         _,
         ) = struct.unpack_from("<II128sII", data)

    def __str__(self):
        return '\n'.join(["protocolVersion: %s" % self.protocolVersion,
                          "keySize: %s" % self.keySize,
                          "key: %s" % repr(self.key),
                          "crc: %s" % self.crc,
                          ])

class ChannelEncryptResult(StructMessage):
    eresult = EResult.Invalid

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        (result,) = struct.unpack_from("<I", data)
        self.eresult = EResult(result)

    def __str__(self):
        return "eresult: %s" % repr(self.eresult)

class ClientLogOnResponse(StructMessage):
    eresult = EResult.Invalid

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        (result,) = struct.unpack_from("<I", data)
        self.eresult = EResult(result)

    def __str__(self):
        return "eresult: %s" % repr(self.eresult)

class ClientVACBanStatus(StructMessage):
    class VACBanRange(object):
        start = 0
        end = 0

        def __str__(self):
            return '\n'.join(["{",
                              "start: %s" % self.start,
                              "end: %d" % self.end,
                              "}",
                              ])

    @property
    def numBans(self):
        return len(self.ranges)

    def __init__(self, data):
        self.ranges = list()
        StructMessage.__init__(self, data)

    def load(self, data):
        buf = StructReader(data)
        numBans, = buf.unpack("<I")

        for _ in range(numBans):
            m = self.VACBanRange()
            self.ranges.append(m)

            m.start, m.end, _ = buf.unpack("<III")

            if m.start > m.end:
                m.start, m.end = m.end, m.start

    def __str__(self):
        text =  ["numBans: %d" % self.numBans]

        for m in self.ranges:  # emulate Protobuf text format
            text.append("ranges " + str(m).replace("\n", "\n    ", 2))

        return '\n'.join(text)

class ClientChatMsg(StructMessage):
    steamIdChatter = 0
    steamIdChatRoom = 0
    ChatMsgType = 0
    text = ""

    def serialize(self):
        rbytes = struct.pack("<QQI",
                             self.steamIdChatter,
                             self.steamIdChatRoom,
                             self.ChatMsgType,
                            )
        # utf-8 encode only when unicode in py2 and str in py3
        rbytes += (self.text.encode('utf-8')
                   if (not isinstance(self.text, str) and bytes is str)
                      or isinstance(self.text, str)
                   else self.text
                  ) + b'\x00'

        return rbytes

    def load(self, data):
        buf = StructReader(data)
        self.steamIdChatter, self.steamIdChatRoom, self.ChatMsgType = buf.unpack("<QQI")
        self.text = buf.read_cstring().decode('utf-8')

    def __str__(self):
        return '\n'.join(["steamIdChatter: %d" % self.steamIdChatter,
                          "steamIdChatRoom: %d" % self.steamIdChatRoom,
                          "ChatMsgType: %d" % self.ChatMsgType,
                          "text: %s" % repr(self.text),
                          ])

class ClientJoinChat(StructMessage):
    steamIdChat = 0
    isVoiceSpeaker = False

    def serialize(self):
        return struct.pack("<Q?",
                           self.steamIdChat,
                           self.isVoiceSpeaker
        )

    def load(self, data):
        (self.steamIdChat,
         self.isVoiceSpeaker
        ) = struct.unpack_from("<Q?", data)

    def __str__(self):
        return '\n'.join(["steamIdChat: %d" % self.steamIdChat,
                          "isVoiceSpeaker: %r" % self.isVoiceSpeaker,
                          ])

class ClientChatMemberInfo(StructMessage):
    steamIdChat = 0
    type = 0
    steamIdUserActedOn = 0
    chatAction = 0
    steamIdUserActedBy = 0

    def serialize(self):
        return struct.pack("<QIQIQ",
                           self.steamIdChat,
                           self.type,
                           self.steamIdUserActedOn,
                           self.chatAction,
                           self.steamIdUserActedBy
        )

    def load(self, data):
        (self.steamIdChat,
         self.type,
         self.steamIdUserActedOn,
         self.chatAction,
         self.steamIdUserActedBy
        ) = struct.unpack_from("<QIQIQ", data)

    def __str__(self):
        return '\n'.join(["steamIdChat: %d" % self.steamIdChat,
                          "type: %r" % self.type,
                          "steamIdUserActedOn: %d" % self.steamIdUserActedOn,
                          "chatAction: %d" % self.chatAction,
                          "steamIdUserActedBy: %d" % self.steamIdUserActedBy
                          ])

class ClientMarketingMessageUpdate2(StructMessage):
    class MarketingMessage(object):
        id = 0
        url = ''
        flags = 0

        def __str__(self):
            return '\n'.join(["{",
                              "id: %s" % self.id,
                              "url: %s" % repr(self.url),
                              "flags: %d" % self.flags,
                              "}",
                              ])

    time = 0

    @property
    def count(self):
        return len(self.messages)

    def __init__(self, data):
        self.messages = list()
        StructMessage.__init__(self, data)

    def load(self, data):
        buf = StructReader(data)
        self.time, count = buf.unpack("<II")

        for _ in range(count):
            m = self.MarketingMessage()
            self.messages.append(m)

            length, m.id = buf.unpack("<IQ")
            m.url = buf.read_cstring().decode('utf-8')
            m.flags = buf.unpack("<I")

    def __str__(self):
        text = ["time: %s" % self.time,
                "count: %d" % self.count,
                ]

        for m in self.messages:  # emulate Protobuf text format
            text.append("messages " + str(m).replace("\n", "\n    ", 3))

        return '\n'.join(text)

class ClientUpdateGuestPassesList(StructMessage):
    eresult = EResult.Invalid
    countGuestPassesToGive = 0
    countGuestPassesToRedeem = 0
    # there is more to parse, but I dont have an sample to figure it out
    # fairly sure this is deprecated anyway since introduction of the invetory system

    def load(self, data):
        (eresult,
         self.countGuestPassesToGive,
         self.countGuestPassesToRedeem,
        ) = struct.unpack_from("<III", data)

        self.eresult = EResult(eresult)

    def __str__(self):
        return '\n'.join(["eresult: %s" % repr(self.eresult),
                          "countGuestPassesToGive: %d" % self.countGuestPassesToGive,
                          "countGuestPassesToRedeem: %d" % self.countGuestPassesToRedeem,
                          ])


class ClientChatEnter(StructMessage):
    steamIdChat = 0
    steamIdFriend = 0
    chatRoomType = 0
    steamIdOwner = 0
    steamIdClan = 0
    chatFlags = 0
    enterResponse = 0
    numMembers = 0
    chatRoomName = ""
    memberList = []

    def __init__(self, data=None):
        if data: self.load(data)

    def load(self, data):
        buf, self.memberList = StructReader(data), list()

        (self.steamIdChat, self.steamIdFriend, self.chatRoomType, self.steamIdOwner,
         self.steamIdClan, self.chatFlags, self.enterResponse, self.numMembers
         ) = buf.unpack("<QQIQQ?II")
        self.chatRoomName = buf.read_cstring().decode('utf-8')

        for _ in range(self.numMembers):
            self.memberList.append(vdf.binary_loads(buf.read(64))['MessageObject'])

        self.UNKNOWN1, = buf.unpack("<I")

    def __str__(self):
        return '\n'.join(["steamIdChat: %d" % self.steamIdChat,
                          "steamIdFriend: %d" % self.steamIdFriend,
                          "chatRoomType: %r" % self.chatRoomType,
                          "steamIdOwner: %d" % self.steamIdOwner,
                          "steamIdClan: %d" % self.steamIdClan,
                          "chatFlags: %r" % self.chatFlags,
                          "enterResponse: %r" % self.enterResponse,
                          "numMembers: %r" % self.numMembers,
                          "chatRoomName: %s" % repr(self.chatRoomName),
        ] + map(lambda x: "memberList: %s" % x, self.memberList))

##################################################################################################

class _ResultStruct(StructMessage):
    eresult = EResult.Invalid

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        eresult, = struct.unpack_from("<I", data)
        self.eresult = EResult(eresult)

    def __str__(self):
        return "eresult: %s" % repr(self.eresult)

##################################################################################################

class ClientRequestValidationMail(StructMessage):
    UNKNOWN1 = b'\x00'

    def serialize(self):
        return self.UNKNOWN1

    def load(self, data):
        self.UNKNOWN1 = data

    def __str__(self):
        return "UNKNOWN1: %s" % repr(self.UNKNOWN1)


class ClientRequestValidationMailResponse(_ResultStruct):
    pass

##################################################################################################

class ClientRequestChangeMail(StructMessage):
    password = ''
    UNKNOWN1 = 0

    def serialize(self):
        return struct.pack("<81sI", self.password[:80].encode('ascii'), self.UNKNOWN1)

    def __str__(self):
        return '\n'.join(["password: %s" % repr(self.password),
                          "UNKNOWN1: %d" % self.UNKNOWN1,
                          ])


class ClientRequestChangeMailResponse(_ResultStruct):
    pass

##################################################################################################

class ClientPasswordChange3(StructMessage):
    password = ''
    new_password = ''
    code = ''

    def serialize(self):
        return (b'\x00'
                + self.password.encode('ascii') + b'\x00'
                + self.new_password.encode('ascii') + b'\x00'
                + self.code.encode('ascii') + b'\x00'
                )

    def __str__(self):
        return '\n'.join(["password: %s" % repr(self.password),
                          "new_password: %s" % repr(self.new_password),
                          "code: %s" % repr(self.code),
                          ])


class ClientPasswordChangeResponse(_ResultStruct):
    pass

