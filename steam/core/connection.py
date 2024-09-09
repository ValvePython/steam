import struct
import logging

import gevent
from gevent import socket
from gevent import queue
from gevent import event
from gevent.select import select as gselect

import ssl
import certifi

from wsproto import WSConnection, events as wsevents
from wsproto.connection import ConnectionType, ConnectionState

logger = logging.getLogger("Connection")


class Connection(object):

    def __init__(self):
        self.socket = None
        self.connected = False
        self.server_addr = None

        self._reader = None
        self._writer = None
        self._readbuf = b''
        self.send_queue = queue.Queue()
        self.recv_queue = queue.Queue()

        self.event_connected = event.Event()

    @property
    def local_address(self):
        return self.socket.getsockname()[0]

    def connect(self, server_addr):
        self._new_socket()

        logger.debug("Attempting connection to %s", str(server_addr))

        try:
            self._connect(server_addr)
        except socket.error:
            return False

        self.server_addr = server_addr
        self.recv_queue.queue.clear()

        self._reader = gevent.spawn(self._reader_loop)
        self._writer = gevent.spawn(self._writer_loop)

        # how this gets set is implementation dependent
        self.event_connected.wait(timeout=10)

        return True

    def disconnect(self):
        if not self.event_connected.is_set():
            return
        self.event_connected.clear()

        self.server_addr = None

        if self._reader:
            self._reader.kill(block=False)
            self._reader = None
        if self._writer:
            self._writer.kill(block=False)
            self._writer = None

        self._readbuf = b''
        self.send_queue.queue.clear()
        self.recv_queue.queue.clear()
        self.recv_queue.put(StopIteration)

        self.socket.close()

        logger.debug("Disconnected.")

    def __iter__(self):
        return self.recv_queue

    def put_message(self, message):
        self.send_queue.put(message)
    
    def _new_socket(self):
        raise TypeError("{}: _new_socket is unimplemented".format(self.__class__.__name__))

    def _connect(self, server_addr):
        raise TypeError("{}: _connect is unimplemented".format(self.__class__.__name__))
    
    def _reader_loop(self):
        raise TypeError("{}: _reader_loop is unimplemented".format(self.__class__.__name__))

    def _writer_loop(self):
        raise TypeError("{}: _writer_loop is unimplemented".format(self.__class__.__name__))

class TCPConnection(Connection):

    MAGIC = b'VT01'
    FMT = '<I4s'
    FMT_SIZE = struct.calcsize(FMT)

    def _new_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _connect(self, server_addr):
        self.socket.connect(server_addr)
        logger.debug("Connected.")
        self.event_connected.set()

    def _read_data(self):
        try:
            return self.socket.recv(16384)
        except socket.error:
            return ''

    def _write_data(self, data):
        self.socket.sendall(data)

    def _writer_loop(self):
        while True:
            message = self.send_queue.get()
            packet = struct.pack(TCPConnection.FMT, len(message), TCPConnection.MAGIC) + message
            try:
                self._write_data(packet)
            except:
                logger.debug("Connection error (writer).")
                self.disconnect()
                return

    def _reader_loop(self):
        while True:
            rlist, _, _ = gselect([self.socket], [], [])

            if self.socket in rlist:
                data = self._read_data()

                if not data:
                    logger.debug("Connection error (reader).")
                    self.disconnect()
                    return

                self._readbuf += data
                self._read_packets()

    def _read_packets(self):
        header_size = TCPConnection.FMT_SIZE
        buf = self._readbuf

        while len(buf) > header_size:
            message_length, magic = struct.unpack_from(TCPConnection.FMT, buf)

            if magic != TCPConnection.MAGIC:
                logger.debug("invalid magic, got %s" % repr(magic))
                self.disconnect()
                return

            packet_length = header_size + message_length

            if len(buf) < packet_length:
                return

            message = buf[header_size:packet_length]
            buf = buf[packet_length:]

            self.recv_queue.put(message)

        self._readbuf = buf

class WebsocketConnection(Connection):

    def __init__(self):
        super(WebsocketConnection, self).__init__()
        self.ws = WSConnection(ConnectionType.CLIENT)
        self.ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        self.event_wsdisconnected = event.Event()

    def _new_socket(self):
        self.raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _connect(self, server_addr):

        host, port = server_addr
        
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            try:
                # tcp socket
                _, _, _, _, sa = res
                self.raw_socket.connect(sa)
                self.socket = self.ssl_ctx.wrap_socket(self.raw_socket, server_hostname=host)
                # websocket
                ws_host = ':'.join(map(str,server_addr))
                ws_send = self.ws.send(wsevents.Request(host=ws_host, target="/cmsocket/"))
                self.socket.sendall(ws_send)
                return
            except socket.error:
                if self.socket is not None:
                    self.socket.close()
    
    def _writer_loop(self):
        while True:
            message = self.send_queue.get()
            try:
                logger.debug("sending message of length {}".format(len(message)))
                self.socket.sendall(self.ws.send(wsevents.Message(data=message)))
            except:
                logger.debug("Connection error (writer).")
                self.disconnect()
                return
    
    def _reader_loop(self):
        while True:
            rlist, _, _ = gselect([self.socket], [], [])

            if self.socket in rlist:

                try:
                    data = self.socket.recv(16384)
                except socket.error:
                    data = ''

                if not data:
                    logger.debug("Connection error (reader).")
                    # A receive of zero bytes indicates the TCP socket has been closed. We
                    # need to pass None to wsproto to update its internal state.
                    logger.debug("Received 0 bytes (connection closed)")
                    self.ws.receive_data(None)
                    # now disconnect
                    self.disconnect()
                    return
                
                logger.debug("Received {} bytes".format(len(data)))
                self.ws.receive_data(data)
                self._handle_events()
    
    def _handle_events(self):
        for event in self.ws.events():
            if isinstance(event, wsevents.AcceptConnection):
                logger.debug("WebSocket negotiation complete. Connected.")
                self.event_connected.set()
            elif isinstance(event, wsevents.RejectConnection):
                logger.debug("WebSocket connection was rejected. That's probably not good.")
            elif isinstance(event, wsevents.TextMessage):
               logger.debug("Received websocket text message of length: {}".format(len(event.data)))
            elif isinstance(event, wsevents.BytesMessage):
                logger.debug("Received websocket bytes message of length: {}".format(len(event.data)))
                self.recv_queue.put(event.data)
            elif isinstance(event, wsevents.Pong):
                logger.debug("Received pong: {}".format(repr(event.payload)))
            elif isinstance(event, wsevents.CloseConnection):
                logger.debug('Connection closed: code={} reason={}'.format(
                    event.code, event.reason
                ))
                if self.ws.state == ConnectionState.REMOTE_CLOSING:
                    self.socket.send(self.ws.send(event.response()))
                self.event_wsdisconnected.set()
            else:
                raise TypeError("Do not know how to handle event: {}".format((event)))

    def disconnect(self):
        self.event_wsdisconnected.clear()
        
        # WebSocket closing handshake
        if self.ws.state == ConnectionState.OPEN:
            logger.debug("Disconnect called. Sending CloseConnection message.")
            self.socket.sendall(self.ws.send(wsevents.CloseConnection(code=1000, reason="sample reason")))
            self.socket.shutdown(socket.SHUT_WR)
            # wait for notification from _reader_loop that the closing response was received
            self.event_wsdisconnected.wait()

        super(WebsocketConnection, self).disconnect()

class UDPConnection(Connection):
    def _new_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
