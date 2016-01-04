import struct
import binascii
import logging
import zipfile

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import gevent
from gevent import event
from gevent import queue
from Crypto.Random import random

from steam.steamid import SteamID
from steam.enums import EResult, EUniverse
from steam.enums.emsg import EMsg
from steam.core import crypto
from steam.core.connection import TCPConnection
from steam.core.msg import is_proto, clear_proto_bit
from steam.core.msg import Msg, MsgProto
from steam.util.events import EventEmitter

server_list = [
    ('162.254.196.41', '27020'), ('162.254.196.40', '27021'),
    ('162.254.196.43', '27019'), ('162.254.196.40', '27018'),
    ('162.254.196.43', '27020'), ('162.254.196.41', '27019'),
    ('162.254.196.41', '27018'), ('162.254.196.42', '27020'),
    ('162.254.196.41', '27017'), ('162.254.196.41', '27021'),
    ('146.66.152.10', '27017'), ('146.66.152.10', '27018'),
    ('146.66.152.11', '27019'), ('146.66.152.11', '27020'),
    ('146.66.152.10', '27019'), ('162.254.197.42', '27018'),
    ('162.254.197.41', '27019'), ('162.254.197.41', '27017'),
    ('208.78.164.14', '27017'), ('208.78.164.14', '27019'),
    ('208.78.164.9', '27019'), ('208.78.164.14', '27018'),
    ('208.78.164.9', '27018'), ('208.78.164.13', '27017'),
]

logger = logging.getLogger("CMClient")


class CMClient(EventEmitter):
    TCP = 0
    UDP = 1

    def __init__(self, protocol=0):
        self.verbose_debug = False

        self._init_attributes()

        self.registered_callbacks = {}

        if protocol == CMClient.TCP:
            self.connection = TCPConnection()
        else:
            raise ValueError("Only TCP is supported")

        self.connection.event_connected.rawlink(self._handle_disconnect)

        self.on(EMsg.ChannelEncryptRequest, self._handle_encrypt_request),
        self.on(EMsg.Multi, self._handle_multi),
        self.on(EMsg.ClientLogOnResponse, self._handle_logon),

    def emit(self, event, *args):
        if event is not None:
            logger.debug("Emit event: %s" % repr(event))
        super(CMClient, self).emit(event, *args)

    def connect(self):
        logger.debug("Connect initiated.")

        while True:
            server_addr = random.choice(server_list)

            if self.connection.connect(server_addr):
                break

            logger.debug("Failed to connect. Retrying...")

        self.connected = True
        self.emit("connected")
        self._recv_loop = gevent.spawn(self._recv_messages)

    def _handle_disconnect(self, event):
        if not event.is_set():
            gevent.spawn(self.disconnect)

    def disconnect(self, reconnect=False):
        if not self.connected:
            return
        self.connected = False

        self.connection.disconnect()

        if self._heartbeat_loop:
            self._heartbeat_loop.kill()
        self._recv_loop.kill()

        self._init_attributes()
        self.emit('disconnected')

        if reconnect:
            gevent.spawn(self.connect)

    def _init_attributes(self):
        self.connected = False

        self.key = None
        self.hmac_secret = None

        self.steam_id = None
        self.session_id = None

        self._recv_loop = None
        self._heartbeat_loop = None

    def send_message(self, message):
        if not isinstance(message, (Msg, MsgProto)):
            raise ValueError("Expected Msg or MsgProto, got %s" % message)

        if self.steam_id:
            message.steamID = self.steam_id
        if self.session_id:
            message.sessionID = self.session_id

        if self.verbose_debug:
            logger.debug("Outgoing: %s\n%s" % (repr(message), str(message)))
        else:
            logger.debug("Outgoing: %s", repr(message))

        data = message.serialize()

        if self.key:
            if self.hmac_secret:
                data = crypto.symmetric_encrypt_HMAC(data, self.key, self.hmac_secret)
            else:
                data = crypto.symmetric_encrypt(data, self.key)

        self.connection.put_message(data)

    def _recv_messages(self):
        for message in self.connection:
            if not self.connected:
                break

            if self.key:
                if self.hmac_secret:
                    try:
                        message = crypto.symmetric_decrypt_HMAC(message, self.key, self.hmac_secret)
                    except RuntimeError as e:
                        logger.exception(e)
                        gevent.spawn(self.disconnect)
                        return
                else:
                    message = crypto.symmetric_decrypt(message, self.key)

            self._parse_message(message)

    def _parse_message(self, message):
            if not self.connected:
                return

            emsg_id, = struct.unpack_from("<I", message)
            emsg = EMsg(clear_proto_bit(emsg_id))

            if emsg in (EMsg.ChannelEncryptRequest,
                        EMsg.ChannelEncryptResponse,
                        EMsg.ChannelEncryptResult,
                        ):

                msg = Msg(emsg, message)
            else:
                try:
                    if is_proto(emsg_id):
                        msg = MsgProto(emsg, message)
                    else:
                        msg = Msg(emsg, message, extended=True)
                except Exception as e:
                    logger.fatal("Failed to deserialize message: %s (is_proto: %s)",
                                 str(emsg),
                                 is_proto(emsg_id)
                                 )
                    logger.exception(e)

            if self.verbose_debug:
                logger.debug("Incoming: %s\n%s" % (repr(msg), str(msg)))
            else:
                logger.debug("Incoming: %s", repr(msg))

            self.emit(emsg, msg)

    def _handle_encrypt_request(self, msg):
        logger.debug("Securing channel")

        try:
            if msg.body.protocolVersion != 1:
                raise RuntimeError("Unsupported protocol version")
            if msg.body.universe != EUniverse.Public:
                raise RuntimeError("Unsupported universe")
        except RuntimeError as e:
            logger.exception(e)
            gevent.spawn(self.disconnect)
            return

        resp = Msg(EMsg.ChannelEncryptResponse)

        challenge = msg.body.challenge
        key, resp.body.key = crypto.generate_session_key(challenge)
        resp.body.crc = binascii.crc32(resp.body.key) & 0xffffffff

        self.send_message(resp)

        msg = self.wait_event(EMsg.ChannelEncryptResult)

        if msg.body.eresult != EResult.OK:
            logger.debug("Failed to secure channel: %s" % msg.body.eresult)
            gevent.spawn(self.disconnect)
            return


        self.key = key
        if challenge:
            logger.debug("Channel secured")
            self.hmac_secret = key[:16]
        else:
            logger.debug("Channel secured (legacy mode)")

        self.emit('channel_secured')

    def _handle_multi(self, msg):
        logger.debug("Unpacking CMsgMulti")

        if msg.body.size_unzipped:
            logger.debug("Unzipping body")

            data = zipfile.ZipFile(StringIO(msg.body.message_body)).read('z')

            if len(data) != msg.body.size_unzipped:
                logger.fatal("Unzipped size mismatch")
                gevent.spawn(self.disconnect)
                return
        else:
            data = msg.body.message_body

        while len(data) > 0:
            size, = struct.unpack_from("<I", data)
            self._parse_message(data[4:4+size])
            data = data[4+size:]

    def _heartbeat(self, interval):
        message = MsgProto(EMsg.ClientHeartBeat)

        while True:
            gevent.sleep(interval)
            self.send_message(message)

    def _handle_logon(self, msg):
        result = msg.body.eresult

        if result in (EResult.TryAnotherCM,
                      EResult.ServiceUnavailable
                      ):
            self.disconnect(True)
            return

        elif result == EResult.OK:
            logger.debug("Logon completed")

            self.steam_id = SteamID(msg.header.steamid)
            self.session_id = msg.header.client_sessionid

            if self._heartbeat_loop:
                self._heartbeat_loop.kill()

            logger.debug("Heartbeat started.")

            interval = msg.body.out_of_game_heartbeat_seconds
            self._heartbeat_loop = gevent.spawn(self._heartbeat, interval)
