import logging
import gevent
from steam.util.events import EventEmitter
from steam.util import set_proto_bit, clear_proto_bit, is_proto
from steam.enums.emsg import EMsg
from steam.enums import EResult
from steam.core.msg import GCMsgHdr, GCMsgHdrProto, MsgProto


class GameCoordinator(EventEmitter):
    def __init__(self, client, app_id):
        self.client = client
        self.app_id = app_id
        self._log = logging.getLogger("GC(appid:%d)" % app_id)

        # listen for GC messages
        self.client.on(EMsg.ClientFromGC, self._handle_from_gc)

    def emit(self, event, *args):
        if event is not None:
            self._log.debug("Emit event: %s" % repr(event))
        super(GameCoordinator, self).emit(event, *args)

    def send(self, header, body):
        message = MsgProto(EMsg.ClientToGC)
        message.header.routing_appid = self.app_id
        message.body.appid = self.app_id
        message.body.msgtype = (set_proto_bit(header.msg)
                                if header.proto
                                else header.msg
                                )
        message.body.payload = header.serialize() + body

        self.client.send(message)

    def _handle_from_gc(self, msg):
        if msg.body.appid != self.app_id:
            return

        emsg = msg.body.msgtype

        if is_proto(emsg):
            header = GCMsgHdrProto(emsg, msg.body.payload)
            header_size = GCMsgHdrProto._size + header.headerLength
        else:
            header = GCMsgHdr(emsg, msg.body.payload)
            header_size = GCMsgHdr._size

        body = msg.body.payload[header_size:]

        self.emit(clear_proto_bit(emsg), header, body)
