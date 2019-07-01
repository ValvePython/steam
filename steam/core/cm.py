import struct
import binascii
import logging
from gzip import GzipFile
from time import time
from collections import defaultdict
from itertools import cycle, count

from io import BytesIO

import gevent
import gevent.socket as socket
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

    EVENT_CONNECTED = 'connected'
    """Connection establed to CM server
    """
    EVENT_DISCONNECTED = 'disconnected'
    """Connection closed
    """
    EVENT_RECONNECT = 'reconnect'
    """Delayed connect

    :param delay: delay in seconds
    :type delay: int
    """
    EVENT_CHANNEL_SECURED = 'channel_secured'
    """After successful completion of encryption handshake
    """
    EVENT_ERROR = 'error'
    """When login is denied

    :param eresult: reason
    :type eresult: :class:`.EResult`
    """
    EVENT_EMSG = 0
    """All incoming messages are emitted with their :class:`.EMsg` number.
    """

    PROTOCOL_TCP = 0                        #: TCP protocol enum
    PROTOCOL_UDP = 1                        #: UDP protocol enum
    verbose_debug = False                   #: print message connects in debug

    auto_discovery = True                   #: enables automatic CM discovery
    cm_servers = None                       #: a instance of :class:`.CMServerList`
    current_server_addr = None              #: (ip, port) tuple
    _seen_logon = False
    _connecting = False
    connected = False                       #: :class:`True` if connected to CM
    channel_secured = False                 #: :class:`True` once secure channel handshake is complete

    channel_key = None                      #: channel encryption key
    channel_hmac = None                     #: HMAC secret

    steam_id = SteamID()                    #: :class:`.SteamID` of the current user
    session_id = None                       #: session id when logged in
    cell_id = 0                             #: cell id provided by CM

    _recv_loop = None
    _heartbeat_loop = None
    _LOG = None

    def __init__(self, protocol=PROTOCOL_TCP):
        self._LOG = logging.getLogger("CMClient")
        self.cm_servers = CMServerList()

        if protocol == CMClient.PROTOCOL_TCP:
            self.connection = TCPConnection()
        else:
            raise ValueError("Only TCP is supported")

        self.on(EMsg.ChannelEncryptRequest, self.__handle_encrypt_request),
        self.on(EMsg.Multi, self.__handle_multi),
        self.on(EMsg.ClientLogOnResponse, self._handle_logon),
        self.on(EMsg.ClientCMList, self._handle_cm_list),

    def emit(self, event, *args):
        if event is not None:
            self._LOG.debug("Emit event: %s" % repr(event))
        super(CMClient, self).emit(event, *args)

    def connect(self, retry=0, delay=0):
        """Initiate connection to CM. Blocks until connected unless ``retry`` is specified.

        :param retry: number of retries before returning. Unlimited when set to ``None``
        :type retry: :class:`int`
        :param delay: delay in seconds before connection attempt
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
            self.emit(self.EVENT_RECONNECT, delay)
            self.sleep(delay)

        self._LOG.debug("Connect initiated.")

        i = count(0)

        while len(self.cm_servers) == 0:
            if not self.auto_discovery or (retry and next(i) >= retry):
                if not self.auto_discovery:
                    self._LOG.error("CM server list is empty. Auto discovery is off.")
                self._connecting = False
                return False

            if not self.cm_servers.bootstrap_from_webapi():
                self.cm_servers.bootstrap_from_dns()

        for i, server_addr in enumerate(cycle(self.cm_servers), start=next(i)-1):
            if retry and i >= retry:
                self._connecting = False
                return False

            start = time()

            if self.connection.connect(server_addr):
                break
            self._LOG.debug("Failed to connect. Retrying...")

            diff = time() - start

            if diff < 5:
                self.sleep(5 - diff)

        self.current_server_addr = server_addr
        self.connected = True
        self.emit(self.EVENT_CONNECTED)
        self._recv_loop = gevent.spawn(self._recv_messages)
        self._connecting = False
        return True

    def disconnect(self):
        """Close connection"""

        if not self.connected:
            return
        self.connected = False

        self.connection.disconnect()

        if self._heartbeat_loop:
            self._heartbeat_loop.kill()
        self._recv_loop.kill()

        self._reset_attributes()

        self.emit(self.EVENT_DISCONNECTED)

    def _reset_attributes(self):
        for name in ['connected',
                     'channel_secured',
                     'channel_key',
                     'channel_hmac',
                     'steam_id',
                     'session_id',
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
            self.idle()

        if not self._seen_logon and self.channel_secured:
            if self.wait_event('disconnected', timeout=5) is not None:
                return

        gevent.spawn(self.disconnect)

    def _parse_message(self, message):
        emsg_id, = struct.unpack_from("<I", message)
        emsg = EMsg(clear_proto_bit(emsg_id))

        if not self.connected and emsg != EMsg.ClientLogOnResponse:
            self._LOG.debug("Dropped unexpected message: %s (is_proto: %s)",
                            repr(emsg),
                            is_proto(emsg_id),
                            )
            return

        if emsg in (EMsg.ChannelEncryptRequest,
                    EMsg.ChannelEncryptResponse,
                    EMsg.ChannelEncryptResult,
                    ):

            msg = Msg(emsg, message, parse=False)
        else:
            try:
                if is_proto(emsg_id):
                    msg = MsgProto(emsg, message, parse=False)
                else:
                    msg = Msg(emsg, message, extended=True, parse=False)
            except Exception as e:
                self._LOG.fatal("Failed to deserialize message: %s (is_proto: %s)",
                                repr(emsg),
                                is_proto(emsg_id)
                                )
                self._LOG.exception(e)
                return

        if self.count_listeners(emsg) or self.verbose_debug:
            msg.parse()

        if self.verbose_debug:
            self._LOG.debug("Incoming: %s\n%s" % (repr(msg), str(msg)))
        else:
            self._LOG.debug("Incoming: %s", repr(msg))

        self.emit(emsg, msg)
        return emsg, msg

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
            self.cm_servers.mark_bad(self.current_server_addr)
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
        self.emit(self.EVENT_CHANNEL_SECURED)

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
            self.sleep(interval)
            self.send(message)

    def _handle_logon(self, msg):
        result = msg.body.eresult

        if result in (EResult.TryAnotherCM,
                      EResult.ServiceUnavailable
                      ):
            self.cm_servers.mark_bad(self.current_server_addr)
            self.disconnect()
        elif result == EResult.OK:
            self._seen_logon = True

            self._LOG.debug("Logon completed")

            self.steam_id = SteamID(msg.header.steamid)
            self.session_id = msg.header.client_sessionid
            self.cell_id = msg.body.cell_id

            if self._heartbeat_loop:
                self._heartbeat_loop.kill()

            self._LOG.debug("Heartbeat started.")

            interval = msg.body.out_of_game_heartbeat_seconds
            self._heartbeat_loop = gevent.spawn(self.__heartbeat, interval)
        else:
            self.emit(self.EVENT_ERROR, EResult(result))
            self.disconnect()

    def _handle_cm_list(self, msg):
        self._LOG.debug("Updating CM list")

        new_servers = zip(map(ip_from_int, msg.body.cm_addresses), msg.body.cm_ports)
        self.cm_servers.clear()
        self.cm_servers.merge_list(new_servers)
        self.cm_servers.cell_id = self.cell_id

    def sleep(self, seconds):
        """Yeild and sleep N seconds. Allows other greenlets to run"""
        gevent.sleep(seconds)

    def idle(self):
        """Yeild in the current greenlet and let other greenlets run"""
        gevent.idle()


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
    last_updated = 0       #: timestamp of when the list was last updated
    cell_id = 0            #: cell id of the server list
    bad_timestamp = 300    #: how long bad mark lasts in seconds

    def __init__(self):
        self._LOG = logging.getLogger("CMServerList")
        self.list = defaultdict(dict)

    def __len__(self):
        return len(self.list)

    def __repr__(self):
        return "<%s: %d servers>" % (self.__class__.__name__, len(self))

    def clear(self):
        """Clears the server list"""
        if len(self.list):
            self._LOG.debug("List cleared.")
        self.list.clear()

    def bootstrap_from_dns(self):
        """
        Fetches CM server list from WebAPI and replaces the current one
        """
        self._LOG.debug("Attempting bootstrap via DNS")

        try:
            answer = socket.getaddrinfo("cm0.steampowered.com",
                                        27017,
                                        socket.AF_INET,
                                        proto=socket.IPPROTO_TCP)
        except Exception as exp:
            self._LOG.error("DNS boostrap failed: %s" % str(exp))
            return False

        servers = list(map(lambda addr: addr[4], answer))

        if servers:
            self.clear()
            self.merge_list(servers)
            return True
        else:
            self._LOG.error("DNS boostrap: cm0.steampowered.com resolved no A records")
            return False

    def bootstrap_from_webapi(self, cell_id=0):
        """
        Fetches CM server list from WebAPI and replaces the current one

        :param cellid: cell id (0 = global)
        :type cellid: :class:`int`
        :return: booststrap success
        :rtype: :class:`bool`
        """
        self._LOG.debug("Attempting bootstrap via WebAPI")

        from steam import webapi
        try:
            resp = webapi.get('ISteamDirectory', 'GetCMList', 1, params={'cellid': cell_id,
                                                                         'http_timeout': 3})
        except Exception as exp:
            self._LOG.error("WebAPI boostrap failed: %s" % str(exp))
            return False

        result = EResult(resp['response']['result'])

        if result != EResult.OK:
            self._LOG.error("GetCMList failed with %s" % repr(result))
            return False

        serverlist = resp['response']['serverlist']
        self._LOG.debug("Recieved %d servers from WebAPI" % len(serverlist))

        def str_to_tuple(serveraddr):
            ip, port = serveraddr.split(':')
            return str(ip), int(port)

        self.clear()
        self.cell_id = cell_id
        self.merge_list(map(str_to_tuple, serverlist))

        return True

    def __iter__(self):
        def cm_server_iter():
            if not self.list:
                self._LOG.error("Server list is empty.")
                return

            good_servers = list(filter(lambda x: x[1]['quality'] == CMServerList.Good,
                                       self.list.items()
                                       ))

            if len(good_servers) == 0:
                self._LOG.debug("No good servers left. Reseting...")
                self.reset_all()
                return

            shuffle(good_servers)

            for server_addr, meta in good_servers:
                yield server_addr

        return cm_server_iter()

    def reset_all(self):
        """Reset status for all servers in the list"""

        self._LOG.debug("Marking all CMs as Good.")

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
        self._LOG.debug("Marking %s as Bad." % repr(server_addr))
        self.list[server_addr].update({'quality': CMServerList.Bad, 'timestamp': time()})

    def merge_list(self, new_list):
        """Add new CM servers to the list

        :param new_list: a list of ``(ip, port)`` tuples
        :type new_list: :class:`list`
        """
        total = len(self.list)

        for ip, port in new_list:
            if (ip, port) not in self.list:
                self.mark_good((ip, port))

        if len(self.list) > total:
            self._LOG.debug("Added %d new CM addresses." % (len(self.list) - total))

        self.last_updated = int(time())
