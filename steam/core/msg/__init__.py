import fnmatch
from steam.core.msg.unified import get_um
from steam.core.msg.structs import get_struct
from steam.core.msg.headers import MsgHdr, ExtendedMsgHdr, MsgHdrProtoBuf, GCMsgHdr, GCMsgHdrProto
from steam.enums import EResult
from steam.enums.emsg import EMsg
from steam.exceptions import SteamError
from steam.protobufs import steammessages_base_pb2
from steam.protobufs import steammessages_clientserver_pb2
from steam.protobufs import steammessages_clientserver_2_pb2
from steam.protobufs import steammessages_clientserver_friends_pb2
from steam.protobufs import steammessages_clientserver_login_pb2


cmsg_lookup_predefined = {
    EMsg.Multi: steammessages_base_pb2.CMsgMulti,
    EMsg.ClientToGC: steammessages_clientserver_2_pb2.CMsgGCClient,
    EMsg.ClientFromGC: steammessages_clientserver_2_pb2.CMsgGCClient,
    EMsg.ClientServiceMethod: steammessages_clientserver_2_pb2.CMsgClientServiceMethodLegacy,
    EMsg.ClientServiceMethodResponse: steammessages_clientserver_2_pb2.CMsgClientServiceMethodLegacyResponse,
    EMsg.ClientGetNumberOfCurrentPlayersDP: steammessages_clientserver_2_pb2.CMsgDPGetNumberOfCurrentPlayers,
    EMsg.ClientGetNumberOfCurrentPlayersDPResponse: steammessages_clientserver_2_pb2.CMsgDPGetNumberOfCurrentPlayersResponse,
#   EMsg.ClientEmailChange4: steammessages_clientserver_2_pb2.CMsgClientEmailChange,
#   EMsg.ClientEmailChangeResponse4: steammessages_clientserver_2_pb2.CMsgClientEmailChangeResponse,
    EMsg.ClientLogonGameServer: steammessages_clientserver_login_pb2.CMsgClientLogon,
    EMsg.ClientCurrentUIMode: steammessages_clientserver_2_pb2.CMsgClientUIMode,
    EMsg.ClientChatOfflineMessageNotification: steammessages_clientserver_2_pb2.CMsgClientOfflineMessageNotification,
}

cmsg_lookup = dict()

for proto_module in [
                    steammessages_clientserver_pb2,
                    steammessages_clientserver_2_pb2,
                    steammessages_clientserver_friends_pb2,
                    steammessages_clientserver_login_pb2,
                    ]:
    cmsg_list = proto_module.__dict__
    cmsg_list = fnmatch.filter(cmsg_list, 'CMsg*')
    cmsg_lookup.update(dict(zip(map(lambda cmsg_name: cmsg_name.lower(), cmsg_list),
                                map(lambda cmsg_name: getattr(proto_module, cmsg_name), cmsg_list)
                               )))


def get_cmsg(emsg):
    """Get protobuf for a given EMsg

    :param emsg: EMsg
    :type  emsg: :class:`steam.enums.emsg.EMsg`, :class:`int`
    :return: protobuf message
    """
    if not isinstance(emsg, EMsg):
        emsg = EMsg(emsg)

    if emsg in cmsg_lookup_predefined:
        return cmsg_lookup_predefined[emsg]
    else:
        enum_name = emsg.name.lower()
        if enum_name.startswith("econ"):  # special case for 'EconTrading_'
            enum_name = enum_name[4:]
        cmsg_name = "cmsg" + enum_name

    return cmsg_lookup.get(cmsg_name, None)

class Msg(object):
    proto = False
    body = None     #: message instance
    payload = None  #: Will contain body payload, if we fail to find correct message class

    def __init__(self, msg, data=None, extended=False, parse=True):
        self.extended = extended
        self.header = ExtendedMsgHdr(data) if extended else MsgHdr(data)
        self.msg = msg

        if data:
            self.payload = data[self.header._size:]

        if parse:
            self.parse()

    def parse(self):
        """Parses :attr:`payload` into :attr:`body` instance"""
        if self.body is None:
            deserializer = get_struct(self.msg)

            if deserializer:
                self.body = deserializer(self.payload)
                self.payload = None
            else:
                self.body = '!!! Failed to resolve message !!!'

    @property
    def msg(self):
        return self.header.msg

    @msg.setter
    def msg(self, value):
        self.header.msg = EMsg(value)

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
        return "<Msg %s%s>" % (
                    repr(self.msg),
                    ' (No Body)' if isinstance(self.body, str) else '',
                    )

    def __str__(self):
        rows = ["Msg"]

        header = str(self.header)
        rows.append("-------------- header --")
        rows.append(header if header else "(empty)")

        body = str(self.body)
        rows.append("---------------- body --")
        rows.append(body if body else "(empty)")

        if self.payload:
            rows.append("------------- payload --")
            rows.append(repr(self.payload))

        return '\n'.join(rows)


class MsgProto(object):
    proto = True
    body = None     #: protobuf message instance
    payload = None  #: Will contain body payload, if we fail to find correct proto message

    def __init__(self, msg, data=None, parse=True):
        self._header = MsgHdrProtoBuf(data)
        self.header = self._header.proto
        self.msg = msg

        if data:
            self.payload = data[self._header._fullsize:]

        if parse:
            self.parse()

    def parse(self):
        """Parses :attr:`payload` into :attr:`body` instance"""
        if self.body is None:
            if self.msg in (EMsg.ServiceMethod, EMsg.ServiceMethodResponse, EMsg.ServiceMethodSendToClient):
                is_resp = False if self.msg == EMsg.ServiceMethod else True
                proto = get_um(self.header.target_job_name, response=is_resp)
            else:
                proto = get_cmsg(self.msg)

            if proto:
                self.body = proto()
                if self.payload:
                    self.body.ParseFromString(self.payload)
                    self.payload = None
            else:
                self.body = '!!! Failed to resolve message !!!'

    @property
    def msg(self):
        return self._header.msg

    @msg.setter
    def msg(self, value):
        self._header.msg = EMsg(value)

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
        return "<MsgProto %s%s>" % (
                    repr(self.msg),
                    ' (No Body)' if isinstance(self.body, str) else '',
                    )

    def __str__(self):
        rows = ["MsgProto %s" % repr(self.msg)]

        header = str(self.header).rstrip()
        rows.append("-------------- header --")
        rows.append(header if header else "(empty)")

        body = str(self.body).rstrip()
        rows.append("---------------- body --")
        rows.append(body if body else "(empty)")

        if self.payload:
            rows.append("------------- payload --")
            rows.append(repr(self.payload))

        return '\n'.join(rows)

