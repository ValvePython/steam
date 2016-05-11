import struct
import binascii
import logging
from gzip import GzipFile
from time import time
from collections import defaultdict

from io import BytesIO

import gevent
from gevent import event, queue
from random import shuffle

from steam.steamid import SteamID
from steam.enums import EResult, EUniverse
from steam.enums.emsg import EMsg
from steam.core import crypto
from steam.core.connection import TCPConnection
from steam.core.msg import Msg, MsgProto
from eventemitter import EventEmitter
from steam.util import ip_from_int, is_proto, clear_proto_bit


class CMClient(EventEmitter):
    """
    CMClient provides a secure message channel to Steam CM servers
    Can be used as mixing or on it's own.

    Incoming messages are parsed and emitted as events using
    their :class:`steam.enums.emsg.EMsg` as event identifier
    """

    TCP = 0                                 #: TCP protocol enum
    UDP = 1                                 #: UDP protocol enum
    verbose_debug = False                   #: print message connects in debug

    servers = None                          #: a instance of :class:`steam.core.cm.CMServerList`
    current_server_addr = None              #: (ip, port) tuple
    _seen_logon = False
    _connecting = False
    connected = False                       #: :class:`True` if connected to CM
    channel_secured = False                 #: :class:`True` once secure channel handshake is complete

    channel_key = None                      #: channel encryption key
    channel_hmac = None                     #: HMAC secret

    steam_id = SteamID()                    #: :class:`steam.steamid.SteamID` of the current user
    session_id = None                       #: session id when logged in
    webapi_authenticate_user_nonce = None   #: nonce for the getting a web session

    _recv_loop = None
    _heartbeat_loop = None
    _LOG = None

    def __init__(self, protocol=0):
        self._LOG = logging.getLogger("CMClient")
        self.servers = CMServerList()

        if protocol == CMClient.TCP:
            self.connection = TCPConnection()
        else:
            raise ValueError("Only TCP is supported")

        self.on(EMsg.ChannelEncryptRequest, self.__handle_encrypt_request),
        self.on(EMsg.Multi, self.__handle_multi),
        self.on(EMsg.ClientLogOnResponse, self._handle_logon),
        self.on(EMsg.ClientCMList, self.__handle_cm_list),

    def emit(self, event, *args):
        if event is not None:
            self._LOG.debug("Emit event: %s" % repr(event))
        super(CMClient, self).emit(event, *args)

    def connect(self, retry=None, delay=0):
        """Initiate connection to CM. Blocks until connected unless ``retry`` is specified.

        :param retry: number of retries before returning. Unlimited when set to ``None``
        :type retry: :class:`int`
        :param delay: delay in secnds before connection attempt
        :type delay: :class:`int`
        :return: successful connection
        :rtype: :class:`bool`
        """
        if self.connected:
            self._LOG.debug("Connect called, but we are connected?")
            return
        if self._connecting:
            self._LOG.debug("Connect called, but we are already connecting.")
            return
        self._connecting = True

        if delay:
            self._LOG.debug("Delayed connect: %d seconds" % delay)
            gevent.sleep(delay)

        self._LOG.debug("Connect initiated.")

        for i, server_addr in enumerate(self.servers):
            if retry is not None and i > retry:
                return False

            start = time()

            if self.connection.connect(server_addr):
                break

            diff = time() - start

            self._LOG.debug("Failed to connect. Retrying...")

            if diff < 5:
                gevent.sleep(5 - diff)

        self.current_server_addr = server_addr
        self.connected = True
        self.emit("connected")
        self._recv_loop = gevent.spawn(self._recv_messages)
        self._connecting = False
        return True

    def disconnect(self):
        """Close connection

        .. note::
            When ``reconnect`` is ``True``, the delay before reconnect is determined
            by exponential backoff algorithm starting from 0 seconds and up to 31 seconds

        :param reconnect: attempt to reconnect
        :type reconnect: :class:`bool`
        :param nodelay: set to ``True`` to ignore reconnect delay
        :type nodelay: :class:`bool`

        Event: ``disconnected``

        Event: ``reconnect`` instead of ``disconnected`` when going to reconnect

        :param delay_seconds: seconds delay before reconnect is attempted
        :type delay_seconds: :class:`int`
        """

        if not self.connected:
            return
        self.connected = False

        self.connection.disconnect()

        if self._heartbeat_loop:
            self._heartbeat_loop.kill()
        self._recv_loop.kill()

        self._reset_attributes()

        self.emit('disconnected')

    def _reset_attributes(self):
        for name in ['connected',
                     'channel_secured',
                     'channel_key',
                     'channel_hmac',
                     'steam_id',
                     'session_id',
                     'webapi_authenticate_user_nonce',
                     '_seen_logon',
                     '_recv_loop',
                     '_heartbeat_loop',
                     ]:
            self.__dict__.pop(name, None)

    def send(self, message):
        """
        Send a message

        :param message: a message instance
        :type message: :class:`steam.core.msg.Msg`, :class:`steam.core.msg.MsgProto`
        """
        if not isinstance(message, (Msg, MsgProto)):
            raise ValueError("Expected Msg or MsgProto, got %s" % message)

        if self.steam_id:
            message.steamID = self.steam_id
        if self.session_id:
            message.sessionID = self.session_id

        if self.verbose_debug:
            self._LOG.debug("Outgoing: %s\n%s" % (repr(message), str(message)))
        else:
            self._LOG.debug("Outgoing: %s", repr(message))

        data = message.serialize()

        if self.channel_key:
            if self.channel_hmac:
                data = crypto.symmetric_encrypt_HMAC(data, self.channel_key, self.channel_hmac)
            else:
                data = crypto.symmetric_encrypt(data, self.channel_key)

        self.connection.put_message(data)

    def _recv_messages(self):
        for message in self.connection:
            if not self.connected:
                break

            if self.channel_key:
                if self.channel_hmac:
                    try:
                        message = crypto.symmetric_decrypt_HMAC(message, self.channel_key, self.channel_hmac)
                    except RuntimeError as e:
                        self._LOG.exception(e)
                        break
                else:
                    message = crypto.symmetric_decrypt(message, self.channel_key)

            gevent.spawn(self._parse_message, message)
            gevent.idle()

        if not self._seen_logon and self.channel_secured:
            if self.wait_event('disconnected', timeout=5) is not None:
                return

        gevent.spawn(self.disconnect)

    def _parse_message(self, message):
        emsg_id, = struct.unpack_from("<I", message)
        emsg = EMsg(clear_proto_bit(emsg_id))

        if not self.connected and emsg != EMsg.ClientLogOnResponse:
            return

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
                self._LOG.fatal("Failed to deserialize message: %s (is_proto: %s)",
                             str(emsg),
                             is_proto(emsg_id)
                             )
                self._LOG.exception(e)

        if self.verbose_debug:
            self._LOG.debug("Incoming: %s\n%s" % (repr(msg), str(msg)))
        else:
            self._LOG.debug("Incoming: %s", repr(msg))

        self.emit(emsg, msg)

    def __handle_encrypt_request(self, req):
        self._LOG.debug("Securing channel")

        try:
            if req.body.protocolVersion != 1:
                raise RuntimeError("Unsupported protocol version")
            if req.body.universe != EUniverse.Public:
                raise RuntimeError("Unsupported universe")
        except RuntimeError as e:
            self._LOG.exception(e)
            gevent.spawn(self.disconnect)
            return

        resp = Msg(EMsg.ChannelEncryptResponse)

        challenge = req.body.challenge
        key, resp.body.key = crypto.generate_session_key(challenge)
        resp.body.crc = binascii.crc32(resp.body.key) & 0xffffffff

        self.send(resp)

        result = self.wait_event(EMsg.ChannelEncryptResult, timeout=5)

        if result is None:
            self.servers.mark_bad(self.current_server_addr)
            gevent.spawn(self.disconnect)
            return

        eresult = result[0].body.eresult

        if eresult != EResult.OK:
            self._LOG.error("Failed to secure channel: %s" % eresult)
            gevent.spawn(self.disconnect)
            return

        self.channel_key = key

        if challenge:
            self._LOG.debug("Channel secured")
            self.channel_hmac = key[:16]
        else:
            self._LOG.debug("Channel secured (legacy mode)")

        self.channel_secured = True
        self.emit('channel_secured')

    def __handle_multi(self, msg):
        self._LOG.debug("Multi: Unpacking")

        if msg.body.size_unzipped:
            self._LOG.debug("Multi: Decompressing payload (%d -> %s)" % (
                len(msg.body.message_body),
                msg.body.size_unzipped,
                ))

            with GzipFile(fileobj=BytesIO(msg.body.message_body)) as f:
                data = f.read()

            if len(data) != msg.body.size_unzipped:
                self._LOG.fatal("Unzipped size mismatch")
                gevent.spawn(self.disconnect)
                return
        else:
            data = msg.body.message_body

        while len(data) > 0:
            size, = struct.unpack_from("<I", data)
            self._parse_message(data[4:4+size])
            data = data[4+size:]

    def __heartbeat(self, interval):
        message = MsgProto(EMsg.ClientHeartBeat)

        while True:
            gevent.sleep(interval)
            self.send(message)

    def _handle_logon(self, msg):
        result = msg.body.eresult

        if result in (EResult.TryAnotherCM,
                      EResult.ServiceUnavailable
                      ):
            self.servers.mark_bad(self.current_server_addr)
            self.disconnect()
        elif result == EResult.OK:
            self._seen_logon = True

            self._LOG.debug("Logon completed")

            self.steam_id = SteamID(msg.header.steamid)
            self.session_id = msg.header.client_sessionid

            self.webapi_authenticate_user_nonce = msg.body.webapi_authenticate_user_nonce

            if self._heartbeat_loop:
                self._heartbeat_loop.kill()

            self._LOG.debug("Heartbeat started.")

            interval = msg.body.out_of_game_heartbeat_seconds
            self._heartbeat_loop = gevent.spawn(self.__heartbeat, interval)
        else:
            self.emit("error", EResult(result))
            self.disconnect()

    def __handle_cm_list(self, msg):
        self._LOG.debug("Updating CM list")

        new_servers = zip(map(ip_from_int, msg.body.cm_addresses), msg.body.cm_ports)
        self.servers.merge_list(new_servers)


class CMServerList(object):
    """
    Managing object for CM servers

    Comes with built in list of CM server to bootstrap a connection

    To get a server address from the list simply iterate over it

    .. code:: python

        servers = CMServerList()
        for server_addr in servers:
            pass

    The good servers are returned first, then bad ones. After failing to connect
    call :meth:`mark_bad` with the server addr. When connection succeeds break
    out of the loop.
    """

    Good = 1
    Bad = 2

    def __init__(self, bad_timespan=300):
        self._log = logging.getLogger("CMServerList")

        self.bad_timespan = bad_timespan
        self.list = defaultdict(dict)

        self.bootstrap_from_builtin_list()

    def bootstrap_from_builtin_list(self):
        """
        Resets the server list to the built in one.
        This method is called during initialization.
        """
        self.list.clear()

        # build-in list
        self.merge_list([('162.254.195.44', 27019), ('146.66.152.11', 27017),
                         ('162.254.196.40', 27017), ('146.66.152.11', 27018),
                         ('162.254.197.41', 27017), ('162.254.197.42', 27018),
                         ('146.66.152.10', 27018),  ('162.254.196.41', 27020),
                         ('185.25.180.14', 27018),  ('162.254.196.43', 27021),
                         ('146.66.155.8', 27018),   ('162.254.196.40', 27018),
                         ('162.254.197.41', 27021), ('162.254.197.42', 27017),
                         ('185.25.180.14', 27017),  ('185.25.182.10', 27018),
                         ('162.254.196.40', 27021), ('208.78.164.9', 27019),
                         ('208.78.164.12', 27018),  ('162.254.196.40', 27019),
                         ('162.254.197.41', 27020), ('208.78.164.14', 27018),
                         ('162.254.195.46', 27019), ('162.254.197.40', 27018),
                         ('155.133.242.8', 27020),  ('162.254.196.41', 27018),
                         ('208.78.164.14', 27019),  ('208.78.164.12', 27017),
                         ('162.254.196.40', 27020), ('162.254.196.42', 27021)
                         ])

    def bootstrap_from_webapi(self, cellid=0):
        """
        Fetches CM server list from WebAPI and replaces the current one

        :param cellid: cell id (0 = global)
        :type cellid: :class:`int`
        :return: booststrap success
        :rtype: :class:`bool`
        """
        from steam import WebAPI

        try:
            api = WebAPI(None)
            resp = api.ISteamDirectory.GetCMList_v1(cellid=cellid)
        except Exception as exp:
            self._log.error("WebAPI boostrap failed: %s" % str(exp))
            return False

        result = EResult(resp['response']['result'])

        if result != EResult.OK:
            self._log.error("GetCMList failed with %s" % repr(result))
            return False

        serverlist = resp['response']['serverlist']
        self._log.debug("Recieved %d servers from WebAPI" % len(serverlist))

        def str_to_tuple(serveraddr):
            ip, port = serveraddr.split(':')
            return str(ip), int(port)

        self.list.clear()
        self.merge_list(map(str_to_tuple, serverlist))

        return True


    def __iter__(self):
        def genfunc():
            while True:
                good_servers = list(filter(lambda x: x[1]['quality'] == CMServerList.Good, self.list.items()))

                if len(good_servers) == 0:
                    self.reset_all()
                    continue

                shuffle(good_servers)

                for server_addr, meta in good_servers:
                    yield server_addr

        return genfunc()

    def reset_all(self):
        """Reset status for all servers in the list"""

        self._log.debug("Marking all CMs as Good.")

        for key in self.list:
            self.mark_good(key)

    def mark_good(self, server_addr):
        """Mark server address as good

        :param server_addr: (ip, port) tuple
        :type server_addr: :class:`tuple`
        """
        self.list[server_addr].update({'quality': CMServerList.Good, 'timestamp': time()})

    def mark_bad(self, server_addr):
        """Mark server address as bad, when unable to connect for example

        :param server_addr: (ip, port) tuple
        :type server_addr: :class:`tuple`
        """
        self._log.debug("Marking %s as Bad." % repr(server_addr))
        self.list[server_addr].update({'quality': CMServerList.Bad, 'timestamp': time()})

    def merge_list(self, new_list):
        """Add new CM servers to the list

        :param new_list: a list of (ip, port) tuples
        :type new_list: :class:`list`
        """
        total = len(self.list)

        for ip, port in new_list:
            self.mark_good((ip, port))

        if total:
            self._log.debug("Added %d new CM addresses." % (len(self.list) - total))
