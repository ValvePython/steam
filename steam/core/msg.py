from importlib import import_module
import re
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
    msg = EMsg.Invalid
    targetJobID = -1
    sourceJobID = -1

    def __init__(self, data=None):
        if data:
            self.load(data)

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
    msg = EMsg.Invalid
    headerSize = 36
    headerVersion = 2
    targetJobID = -1
    sourceJobID = -1
    headerCanary = 239
    steamID = -1
    sessionID = -1

    def __init__(self, data=None):
        if data:
            self.load(data)

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


class Msg(object):
    proto = False

    def __init__(self, msg, data=None, extended=False):
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

cmsg_lookup_predefined = {
    EMsg.Multi: steammessages_base_pb2.CMsgMulti,
    EMsg.ClientToGC: steammessages_clientserver_2_pb2.CMsgGCClient,
    EMsg.ClientFromGC: steammessages_clientserver_2_pb2.CMsgGCClient,
    EMsg.ServiceMethod: steammessages_clientserver_2_pb2.CMsgClientServiceMethod,
    EMsg.ServiceMethodResponse: steammessages_clientserver_2_pb2.CMsgClientServiceMethodResponse,
}

def get_cmsg(emsg):
    """Get protobuf for a given EMsg

    :param emsg: EMsg
    :type emsg: :class:`steam.enums.emsg.EMsg`, :class:`int`
    :return: protobuf message
    """
    global cmsg_lookup, cmsg_lookup2

    if emsg in cmsg_lookup_predefined:
        return cmsg_lookup_predefined[emsg]
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
    proto = True
    body = "!!! NO BODY !!!"

    def __init__(self, msg, data=None):
        self._header = MsgHdrProtoBuf(data)
        self.msg = self._header.msg = msg
        self.header = self._header.proto

        if msg == EMsg.ServiceMethod:
            proto = get_um(self.header.target_job_name)
            if proto:
                self.body = proto()
            else:
                self.body = '!! Can\'t resolve ServiceMethod: %s !!' % repr(self.header.target_job_name)
        else:
            proto = get_cmsg(msg)

        if proto:
            self.body = proto()

            if data:
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
    protocolVersion = 1
    universe = EUniverse.Invalid
    challenge = b''

    def __init__(self, data=None):
        if data:
            self.load(data)

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


class ChannelEncryptResponse:
    protocolVersion = 1
    keySize = 128
    key = ''
    crc = 0

    def __init__(self, data=None):
        if data:
            self.load(data)

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
    eresult = EResult.Invalid

    def __init__(self, data=None):
        if data:
            self.load(data)

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        (result,) = struct.unpack_from("<I", data)
        self.eresult = EResult(result)

    def __str__(self):
        return "result: %s" % repr(self.eresult)

class ClientLogOnResponse:
    eresult = EResult.Invalid

    def __init__(self, data=None):
        if data:
            self.load(data)

    def serialize(self):
        return struct.pack("<I", self.eresult)

    def load(self, data):
        (result,) = struct.unpack_from("<I", data)
        self.eresult = EResult(result)

    def __str__(self):
        return "eresult: %s" % repr(self.eresult)


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

service_lookup = {
    'Broadcast':           'steam.protobufs.steammessages_broadcast_pb2',
    'Cloud':               'steam.protobufs.steammessages_cloud_pb2',
    'DNReport':            'steam.protobufs.steammessages_cloud_pb2',
    'Credentials':         'steam.protobufs.steammessages_credentials_pb2',
    'ContentBuilder':      'steam.protobufs.steammessages_depotbuilder_pb2',
    'DeviceAuth':          'steam.protobufs.steammessages_deviceauth_pb2',
    'Econ':                'steam.protobufs.steammessages_econ_pb2',
    'GameNotifications':   'steam.protobufs.steammessages_gamenotifications_pb2',
    'GameServers':         'steam.protobufs.steammessages_gameservers_pb2',
    'Inventory':           'steam.protobufs.steammessages_inventory_pb2',
    'Community':           'steam.protobufs.steammessages_linkfilter_pb2',
    'Offline':             'steam.protobufs.steammessages_offline_pb2',
    'Parental':            'steam.protobufs.steammessages_parental_pb2',
    'PartnerApps':         'steam.protobufs.steammessages_partnerapps_pb2',
    'PhysicalGoods':       'steam.protobufs.steammessages_physicalgoods_pb2',
    'PlayerClient':        'steam.protobufs.steammessages_player_pb2',
    'Player':              'steam.protobufs.steammessages_player_pb2',
    'PublishedFile':       'steam.protobufs.steammessages_publishedfile_pb2',
    'KeyEscrow':           'steam.protobufs.steammessages_secrets_pb2',
    'TwoFactor':           'steam.protobufs.steammessages_twofactor_pb2',
    'MsgTest':             'steam.protobufs.steammessages_unified_test_pb2',
    'Video':               'steam.protobufs.steammessages_video_pb2',
}

method_lookup = {
}

def get_um(method_name, response=False):
    """Get protobuf for given method name

    :param method_name: full method name (e.g. ``Player.GetGameBadgeLevels#1``)
    :type method_name: :class:`str`
    :param response: whether to return proto for response or request
    :type response: :class:`bool`
    :return: protobuf message
    """
    key = (method_name, response)

    if key not in method_lookup:
        match = re.findall(r'^([a-z]+)\.([a-z]+)#(\d)?$', method_name, re.I)
        if not match:
            return None

        interface, method, version = match[0]

        if interface not in service_lookup:
            raise None

        package = import_module(service_lookup[interface])

        service = getattr(package, interface, None)
        if service is None:
            return None

        for method_desc in service.GetDescriptor().methods:
            name = "%s.%s#%d" % (interface, method_desc.name, 1)

            method_lookup[(name, False)] = getattr(package, method_desc.input_type.full_name, None)
            method_lookup[(name, True)] = getattr(package, method_desc.output_type.full_name, None)

    return method_lookup[key]
