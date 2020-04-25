"""Classes to (de)serialize message headers"""
import struct
from steam.enums.emsg import EMsg
from steam.protobufs import steammessages_base_pb2
from steam.protobufs import gc_pb2
from steam.utils.proto import set_proto_bit, clear_proto_bit


class MsgHdr:
    _size = struct.calcsize("<Iqq")
    msg = EMsg.Invalid
    targetJobID = -1
    sourceJobID = -1

    def __init__(self, data=None):
        if data: self.load(data)

    def serialize(self):
        return struct.pack("<Iqq", self.msg, self.targetJobID, self.sourceJobID)

    def load(self, data):
        (msg, self.targetJobID, self.sourceJobID) = struct.unpack_from("<Iqq", data)
        self.msg = EMsg(msg)

    def __str__(self):
        return '\n'.join(["msg: %s" % repr(self.msg),
                          "targetJobID: %s" % self.targetJobID,
                          "sourceJobID: %s" % self.sourceJobID,
                          ])

class ExtendedMsgHdr:
    _size = struct.calcsize("<IBHqqBqi")
    msg = EMsg.Invalid
    headerSize = 36
    headerVersion = 2
    targetJobID = -1
    sourceJobID = -1
    headerCanary = 239
    steamID = -1
    sessionID = -1

    def __init__(self, data=None):
        if data: self.load(data)

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
    _size = _fullsize = struct.calcsize("<II")
    msg = EMsg.Invalid

    def __init__(self, data=None):
        self.proto = steammessages_base_pb2.CMsgProtoBufHeader()

        if data:
            self.load(data)

    def serialize(self):
        proto_data = self.proto.SerializeToString()
        return struct.pack("<II", set_proto_bit(self.msg), len(proto_data)) + proto_data

    def load(self, data):
        msg, proto_length = struct.unpack_from("<II", data)

        self.msg = EMsg(clear_proto_bit(msg))
        size = MsgHdrProtoBuf._size
        self._fullsize = size + proto_length
        self.proto.ParseFromString(data[size:self._fullsize])


class GCMsgHdr:
    _size = struct.calcsize("<Hqq")
    proto = None
    headerVersion = 1
    targetJobID = -1
    sourceJobID = -1

    def __init__(self, msg, data=None):
        self.msg = clear_proto_bit(msg)

        if data:
            self.load(data)

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
    headerLength = 0

    def __init__(self, msg, data=None):
        self.proto = gc_pb2.CMsgProtoBufHeader()
        self.msg = clear_proto_bit(msg)

        if data:
            self.load(data)

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
