"""
Example usage for messages to the Dota 2 GC.

.. code:: python

    from steam import SteamClient
    from steam.client.gc import GameCoordinator

    client = SteamClient()
    gc = GameCoordinator(client, 570)

    @gc.on(None)
    def handle_any_gc_message(header, body):
        pass

    @gc.on(4004)  # EMsgGCClientWelcome
    def handle_client_welcome(header, body):
        passs

"""
import logging
import gevent
from eventemitter import EventEmitter
from steam.util import set_proto_bit, clear_proto_bit, is_proto
from steam.enums.emsg import EMsg
from steam.enums import EResult
from steam.core.msg import GCMsgHdr, GCMsgHdrProto, MsgProto


class GameCoordinator(EventEmitter):
    """
    GameCoordinator is used to proxy messages from/to GC

    :param steam_client: steam client instance
    :type steam_client: :class:`steam.client.SteamClient`
    :param app_id: app id of the application
    :type app_id: :class:`int`
    """

    def __init__(self, steam_client, app_id):
        self.steam = steam_client
        self.app_id = app_id
        self._log = logging.getLogger("GC(appid:%d)" % app_id)

        # listen for GC messages
        self.steam.on(EMsg.ClientFromGC, self._handle_from_gc)

    def emit(self, event, *args):
        if event is not None:
            self._log.debug("Emit event: %s" % repr(event))
        super(GameCoordinator, self).emit(event, *args)

    def send(self, header, body):
        """
        Send a message to GC

        :param header: message header
        :type header: :class:`steam.core.msg.GCMsgHdr`
        :param body: serialized body of the message
        :type body: :class:`bytes`
        """
        message = MsgProto(EMsg.ClientToGC)
        message.header.routing_appid = self.app_id
        message.body.appid = self.app_id
        message.body.msgtype = (set_proto_bit(header.msg)
                                if header.proto
                                else header.msg
                                )
        message.body.payload = header.serialize() + body

        self.steam.send(message)

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
