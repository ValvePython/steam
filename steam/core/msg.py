import struct
import fnmatch
from steam.enums import EResult, EUniverse
from steam.enums.emsg import EMsg
from steam.protobufs import steammessages_base_pb2
from steam.protobufs import steammessages_clientserver_pb2
from steam.protobufs import steammessages_clientserver_2_pb2
from steam.protobufs import gc_pb2
from steam.util import set_proto_bit, clear_proto_bit


class MsgHdr:
    _size = struct.calcsize("<Iqq")

    def __init__(self, data=None):
        if data:
            self.load(data)
        else:
            self.msg = EMsg.Invalid
            self.targetJobID = -1
            self.sourceJobID = -1

    def serialize(self):
        return struct.pack("<Iqq",
                           self.msg,
                           self.targetJobID,
                           self.sourceJobID,
                           )

    def load(self, data):
        (msg,
         self.targetJobID,
         self.sourceJobID,
         ) = struct.unpack_from("<Iqq", data)

        self.msg = EMsg(msg)

    def __str__(self):
        return '\n'.join(["msg: %s" % repr(self.msg),
                          "targetJobID: %s" % self.targetJobID,
                          "sourceJobID: %s" % self.sourceJobID,
                          ])


class ExtendedMsgHdr:
    _size = struct.calcsize("<IBHqqBqi")

    def __init__(self, data=None):
        if data:
            self.load(data)
        else:
            self.msg = EMsg.Invalid
            self.headerSize = 36
            self.headerVersion = 2
            self.targetJobID = -1
            self.sourceJobID = -1
            self.headerCanary = 239
            self.steamID = -1
            self.sessionID = -1

    def serialize(self):
        return struct.pack("<IBHqqBqi",
                           self.msg,
                           self.headerSize,
                           self.headerVersion,
                           self.targetJobID,
                           self.sourceJobID,
                           self.headerCanary,
                           self.steamID,
                           self.sessionID,
                           )

    def load(self, data):
        (msg,
         self.headerSize,
         self.headerVersion,
         self.targetJobID,
         self.sourceJobID,
         self.headerCanary,
         self.steamID,
         self.sessionID,
         ) = struct.unpack_from("<IBHqqBqi", data)

        self.msg = EMsg(msg)

        if self.headerSize != 36 or self.headerVersion != 2:
            raise RuntimeError("Failed to parse header")

    def __str__(self):
        return '\n'.join(["msg: %s" % self.msg,
                          "headerSize: %s" % self.headerSize,
                          "headerVersion: %s" % self.headerVersion,
                          "targetJobID: %s" % self.targetJobID,
                          "sourceJobID: %s" % self.sourceJobID,
                          "headerCanary: %s" % self.headerCanary,
                          "steamID: %s" % self.steamID,
                          "sessionID: %s" % self.sessionID,
                          ])


class MsgHdrProtoBuf:
    _size = struct.calcsize("<II")

    def __init__(self, data=None):
        self.proto = steammessages_base_pb2.CMsgProtoBufHeader()

        if data:
            self.load(data)
        else:
            self.msg = EMsg.Invalid

    def serialize(self):
        proto_data = self.proto.SerializeToString()
        return struct.pack("<II", set_proto_bit(self.msg), len(proto_data)) + proto_data

    def load(self, data):
        msg, proto_length = struct.unpack_from("<II", data)

        self.msg = EMsg(clear_proto_bit(msg))
        size = MsgHdrProtoBuf._size
        self._fullsize = size + proto_length
        self.proto.ParseFromString(data[size:self._fullsize])


class Msg(object):
    def __init__(self, msg, data=None, extended=False):
        self.proto = False
        self.extended = extended
        self.header = ExtendedMsgHdr(data) if extended else MsgHdr(data)
        self.header.msg = msg
        self.msg = msg

        if data:
            data = data[self.header._size:]

        if msg == EMsg.ChannelEncryptRequest:
            self.body = ChannelEncryptRequest(data)
        elif msg == EMsg.ChannelEncryptResponse:
            self.body = ChannelEncryptResponse(data)
        elif msg == EMsg.ChannelEncryptResult:
            self.body = ChannelEncryptResult(data)
        elif msg == EMsg.ClientLogOnResponse:
            self.body = ClientLogOnResponse(data)
        else:
            self.body = None

    def serialize(self):
        return self.header.serialize() + self.body.serialize()

    @property
    def steamID(self):
        return (self.header.steamID
                if isinstance(self.header, ExtendedMsgHdr)
                else None
                )

    @steamID.setter
    def steamID(self, value):
        if isinstance(self.header, ExtendedMsgHdr):
            self.header.steamID = value

    @property
    def sessionID(self):
        return (self.header.sessionID
                if isinstance(self.header, ExtendedMsgHdr)
                else None
                )

    @sessionID.setter
    def sessionID(self, value):
        if isinstance(self.header, ExtendedMsgHdr):
            self.header.sessionID = value

    def __repr__(self):
        return "<Msg %s>" % repr(self.msg)

    def __str__(self):
        rows = ["Msg"]

        header = str(self.header)
        if header:
            rows.append("-------------- header --")
            rows.append(header)

        body = str(self.body)
        if body:
            rows.append("---------------- body --")
            rows.append(body)

        if len(rows) == 1:
            rows[0] += " (empty)"

        return '\n'.join(rows)


cmsg_lookup = None
cmsg_lookup2 = None


def get_cmsg(emsg):
    global cmsg_lookup, cmsg_lookup2

    if emsg == EMsg.Multi:
        return steammessages_base_pb2.CMsgMulti
    elif emsg in (EMsg.ClientToGC, EMsg.ClientFromGC):
        return steammessages_clientserver_2_pb2.CMsgGCClient
    else:
        cmsg_name = "cmsg" + str(emsg).split('.', 1)[1].lower()

    if not cmsg_lookup:
        cmsg_list = steammessages_clientserver_pb2.__dict__
        cmsg_list = fnmatch.filter(cmsg_list, 'CMsg*')
        cmsg_lookup = dict(zip(map(lambda x: x.lower(), cmsg_list), cmsg_list))

    name = cmsg_lookup.get(cmsg_name, None)
    if name:
        return getattr(steammessages_clientserver_pb2, name)

    if not cmsg_lookup2:
        cmsg_list = steammessages_clientserver_2_pb2.__dict__
        cmsg_list = fnmatch.filter(cmsg_list, 'CMsg*')
        cmsg_lookup2 = dict(zip(map(lambda x: x.lower(), cmsg_list), cmsg_list))

    name = cmsg_lookup2.get(cmsg_name, None)
    if name:
        return getattr(steammessages_clientserver_2_pb2, name)

    return None


class MsgProto(object):
    def __init__(self, msg, data=None):
        self.proto = True
        self._header = MsgHdrProtoBuf(data)
        self._header.msg = msg

        self.msg = msg
        self.header = self._header.proto
        proto = get_cmsg(msg)

        if msg == EMsg.ServiceMethod:
            self.body = "!!NOT IMPLEMENTED!!"
        else:
            self.body = proto()

        if data and proto is not None:
            data = data[self._header._fullsize:]
            self.body.ParseFromString(data)

    def serialize(self):
        return self._header.serialize() + self.body.SerializeToString()

    @property
    def steamID(self):
        return self.header.steamid

    @steamID.setter
    def steamID(self, value):
        self.header.steamid = value

    @property
    def sessionID(self):
        return self.header.client_sessionid

    @sessionID.setter
    def sessionID(self, value):
        self.header.client_sessionid = value

    def __repr__(self):
        return "<MsgProto %s>" % repr(self.msg)

    def __str__(self):
        rows = ["MsgProto"]

        header = str(self.header).rstrip()
        if header:
            rows.append("-------------- header --")
            rows.append(header)

        body = str(self.body).rstrip()
        if body:
            rows.append("---------------- body --")
            rows.append(body)

        if len(rows) == 1:
            rows[0] += " (empty)"

        return '\n'.join(rows)


class ChannelEncryptRequest:
    def __init__(self, data=None):
        if data:
            self.load(data)
        else:
            self.protocolVersion = 1
            self.universe = EUniverse.Invalid
            self.challenge = ''

    def serialize(self):
        return struct.pack("<II", self.protocolVersion, self.universe)

    def load(self, data):
        (self.protocolVersion,
         universe,
         ) = struct.unpack_from("<II", data)

        self.universe = EUniverse(universe)

        if len(data) >= 16:
            self.challenge = data[8:]

    def __str__(self):
        return '\n'.join(["protocolVersion: %s" % self.protocolVersion,
                          "universe: %s" % repr(self.universe),
                          "challenge: %s" % repr(self.challenge),
                          ])


class ChannelEncryptResponse:
    def __init__(self, data=None):
        if data:
            self.load(data)
        else:
            self.protocolVersion = 1
            self.keySize = 128
            self.key = ''
            self.crc = 0

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


class ChannelEncryptResult:
    def __init__(self, data=None):
        if data:
            self.load(data)
        else:
            self.eresult = EResult.Invalid

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        (result,) = struct.unpack_from("<I", data)
        self.eresult = EResult(result)

    def __str__(self):
        return "result: %s" % repr(self.eresult)

class ClientLogOnResponse:
    def __init__(self, data=None):
        if data:
            self.load(data)
        else:
            self.eresult = EResult.Invalid

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        (result,) = struct.unpack_from("<I", data)
        self.eresult = EResult(result)

    def __str__(self):
        return "eresult: %s" % repr(self.eresult)


class GCMsgHdr:
    _size = struct.calcsize("<Hqq")

    def __init__(self, msg, data=None):
        self.proto = None
        self.msg = clear_proto_bit(msg)

        if data:
            self.load(data)
        else:
            self.headerVersion = 1
            self.targetJobID = -1
            self.sourceJobID = -1

    def serialize(self):
        return struct.pack("<Hqq",
                           self.headerVersion,
                           self.targetJobID,
                           self.sourceJobID,
                           )

    def load(self, data):
        (self.headerVersion,
         self.targetJobID,
         self.sourceJobID,
         ) = struct.unpack_from("<Hqq", data)

    def __str__(self):
        return '\n'.join(["headerVersion: %s" % self.headerVersion,
                          "targetJobID: %s" % self.targetJobID,
                          "sourceJobID: %s" % self.sourceJobID,
                          ])

class GCMsgHdrProto:
    _size = struct.calcsize("<Ii")

    def __init__(self, msg, data=None):
        self.proto = gc_pb2.CMsgProtoBufHeader()

        if data:
            self.load(data)
        else:
            self.msg = clear_proto_bit(msg)
            self.headerLength = 0


    def serialize(self):
        proto_data = self.proto.SerializeToString()
        self.headerLength = len(proto_data)

        return struct.pack("<Ii",
                           set_proto_bit(self.msg),
                           self.headerLength,
                           ) + proto_data

    def load(self, data):
        (msg,
         self.headerLength,
         ) = struct.unpack_from("<Ii", data)

        self.msg = clear_proto_bit(msg)

        if self.headerLength:
            x = GCMsgHdrProto._size
            self.proto.ParseFromString(data[x:x+self.headerLength])

    def __str__(self):
        resp = ["msg: %s" % self.msg,
                "headerLength: %s" % self.headerLength,
                ]

        proto = str(self.proto)

        if proto:
            resp.append('-- proto --')
            resp.append(proto)

        return '\n'.join(resp)
