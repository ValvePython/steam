import fnmatch
from steam.core.msg.unified import get_um
from steam.core.msg.structs import get_struct
from steam.core.msg.headers import MsgHdr, ExtendedMsgHdr, MsgHdrProtoBuf, GCMsgHdr, GCMsgHdrProto
from steam.enums.emsg import EMsg
from steam.protobufs import steammessages_base_pb2
from steam.protobufs import steammessages_clientserver_pb2
from steam.protobufs import steammessages_clientserver_2_pb2
from steam.protobufs import steammessages_clientserver_friends_pb2
from steam.protobufs import steammessages_clientserver_login_pb2


cmsg_lookup_predefined = {
    EMsg.Multi: steammessages_base_pb2.CMsgMulti,
    EMsg.ClientToGC: steammessages_clientserver_2_pb2.CMsgGCClient,
    EMsg.ClientFromGC: steammessages_clientserver_2_pb2.CMsgGCClient,
    EMsg.ServiceMethod: steammessages_clientserver_2_pb2.CMsgClientServiceMethod,
    EMsg.ServiceMethodResponse: steammessages_clientserver_2_pb2.CMsgClientServiceMethodResponse,
    EMsg.ClientGetNumberOfCurrentPlayersDP: steammessages_clientserver_2_pb2.CMsgDPGetNumberOfCurrentPlayers,
    EMsg.ClientGetNumberOfCurrentPlayersDPResponse: steammessages_clientserver_2_pb2.CMsgDPGetNumberOfCurrentPlayersResponse,
    EMsg.ClientCreateAccountProto: steammessages_clientserver_2_pb2.CMsgClientCreateAccount,
    EMsg.ClientCreateAccountProtoResponse: steammessages_clientserver_2_pb2.CMsgClientCreateAccountResponse,
    EMsg.ClientEmailChange4: steammessages_clientserver_2_pb2.CMsgClientEmailChange,
    EMsg.ClientEmailChangeResponse4: steammessages_clientserver_2_pb2.CMsgClientEmailChangeResponse,
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
    :type emsg: :class:`steam.enums.emsg.EMsg`, :class:`int`
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
    body = '!!! NO BODY !!!'

    def __init__(self, msg, data=None, extended=False):
        self.extended = extended
        self.header = ExtendedMsgHdr(data) if extended else MsgHdr(data)
        self.header.msg = msg
        self.msg = msg

        if data:
            data = data[self.header._size:]

        deserializer = get_struct(msg)

        if deserializer:
            self.body = deserializer(data)

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


