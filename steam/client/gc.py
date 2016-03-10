"""
:class:`GameCoordinator` is used to proxy messages from/to GC.
It takes care of the encapsulation details, but on it's own is not
enough to communicate with a given GC.

Example usage for sending client hello to Dota 2's GC.

.. code:: python

    import myDotaModule
    from steam import SteamClient
    from steam.core.msg import GCMsgHdrProto
    from steam.client.gc import GameCoordinator

    client = SteamClient()

    # login logic etc

    gc = GameCoordinator(client, 570)

    @gc.on(None)
    def handle_any_gc_message(header, body):
        pass

    @gc.on(4004)  # EMsgGCClientWelcome
    def handle_client_welcome(header, body):
        message = myDotaModule.gcsdk_gcmessages_pb2.CMsgClientWelcome()
        message.ParseFromString(body)

    # indicate to steam that we are playing Dota 2
    client.games_played([570])

    # send client hello
    header = GCMsgHdrProto(4006)  # EMsgGCClientHello
    body = myDotaModule.gcsdk_gcmessages_pb2.CMsgClientHello()
    gc.send(header, body.SerializeToString())

The above code assumes that we have a ``myDotaModule`` that contains the appropriate
data structures, which can be used to (de)serialize messages. For example, protobufs.
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
    ``GameCoordinator`` is used to proxy messages from/to GC

    :param steam_client: steam client instance
    :type steam_client: :class:`steam.client.SteamClient`
    :param app_id: app id of the application
    :type app_id: :class:`int`

    Incoming messages are emitted as events using their ``EMsg`` as an event identifier.

    :param header: message header
    :type header: :class:`steam.core.msg.GCMsgHdr`
    :param body: raw message body
    :type body: :class:`bytes`
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
