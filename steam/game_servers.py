# -*- coding: utf-8 -*-
r""" Master Server Query Protocol

This module implements the legacy Steam master server protocol.

https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol

Nowadays games query servers through Steam. See :any:`steam.client.builtins.gameservers`

Filters
-------

.. note::
    Multiple filters can be joined to together (Eg. ``\appid\730\white\1\empty\1``)

=========================== =========================================================================================================================
Filter code                 What it does
=========================== =========================================================================================================================
\\nor\\[x]                  A special filter, specifies that servers matching any of the following [x] conditions should not be returned
\\nand\\[x]                 A special filter, specifies that servers matching all of the following [x] conditions should not be returned
\\dedicated\\1              Servers running dedicated
\\secure\\1                 Servers using anti-cheat technology (VAC, but potentially others as well)
\\gamedir\\[mod]            Servers running the specified modification (ex. cstrike)
\\map\\[map]                Servers running the specified map (ex. cs_italy)
\\linux\\1                  Servers running on a Linux platform
\\password\\0               Servers that are not password protected
\\empty\\1                  Servers that are not empty
\\full\\1                   Servers that are not full
\\proxy\\1                  Servers that are spectator proxies
\\appid\\[appid]            Servers that are running game [appid]
\\napp\\[appid]             Servers that are NOT running game [appid] (This was introduced to block Left 4 Dead games from the Steam Server Browser)
\\noplayers\\1              Servers that are empty
\\white\\1                  Servers that are whitelisted
\\gametype\\[tag,...]       Servers with all of the given tag(s) in sv_tags
\\gamedata\\[tag,...]       Servers with all of the given tag(s) in their 'hidden' tags (L4D2)
\\gamedataor\\[tag,...]     Servers with any of the given tag(s) in their 'hidden' tags (L4D2)
\\name_match\\[hostname]    Servers with their hostname matching [hostname] (can use * as a wildcard)
\\version_match\\[version]  Servers running version [version] (can use * as a wildcard)
\\collapse_addr_hash\\1     Return only one server for each unique IP address matched
\\gameaddr\\[ip]            Return only servers on the specified IP address (port supported and optional)
=========================== =========================================================================================================================

Examples
--------

Query HL Master

.. code:: python

    >>> for server_addr in gs.query_master(r'\appid\730\white\1', max_servers=3):
    ...     print(server_addr)
    ...
    ('146.66.152.197', 27073)
    ('146.66.153.124', 27057)
    ('146.66.152.56', 27053)

Team Fortress 2 (Source)

.. code:: python

    >>> from steam import game_servers as gs
    >>> server_addr = next(gs.query_master(r'\appid\40\empty\1\secure\1'))  # single TF2 Server
    >>> gs.a2s_ping(server_addr)
    68.60899925231934
    >>> gs.a2s_info(server_addr)
    {'_ping': 74.61714744567871,
     '_type': 'source',
     'app_id': 40,
     'bots': 0,
     'environment': 'l',
     'folder': u'dmc',
     'game': u'DMC\t\t\t\t\t\t\t\t1',
     'map': u'crossfire',
     'max_players': 32,
     'name': u'\t\t\u2605\t\t All Guns party \u2605\t \tCrossfire 24/7\t\t',
     'players': 21,
     'protocol': 48,
     'server_type': 'd',
     'vac': 1,
     'visibility': 0}
    >>> gs.a2s_players(server_addr)
    [{'duration': 192.3097381591797, 'index': 0, 'name': '(2)Player', 'score': 4},
     {'duration': 131.6618194580078, 'index': 1, 'name': 'BOLT', 'score': 2},
     {'duration': 16.548809051513672, 'index': 2, 'name': 'Alpha', 'score': 0},
     {'duration': 1083.1539306640625, 'index': 3, 'name': 'Player', 'score': 29},
     {'duration': 446.7716064453125, 'index': 4, 'name': '(1)Player', 'score': 11},
     {'duration': 790.9588012695312, 'index': 5, 'name': 'ИВАНГАЙ', 'score': 11}]
    >>> gs.a2s_rules(server_addr)
    {'amx_client_languages': 1,
     'amx_nextmap': 'crossfire',
     'amx_timeleft': '00:00',
     'amxmodx_version': '1.8.2',
     ....

Ricohet (GoldSrc)

.. code:: python

    >>> from steam import game_servers as gs
    >>> server_addr = next(gs.query_master(r'\appid\60'))  # get a single ip from hl2 master
    >>> gs.a2s_info(server_addr, force_goldsrc=True)       # only accept goldsrc response
    {'_ping': 26.59320831298828,
     '_type': 'goldsrc',
     'address': '127.0.0.1:27050',
     'bots': 0,
     'ddl': 0,
     'download_link': '',
     'environment': 'w',
     'folder': 'ricochet',
     'game': 'Ricochet',
     'link': '',
     'map': 'rc_deathmatch2',
     'max_players': 32,
     'mod': 1,
     'name': 'Anitalink.com Ricochet',
     'players': 1,
     'protocol': 47,
     'server_type': 'd',
     'size': 0,
     'type': 1,
     'vac': 1,
     'version': 1,
     'visibility': 0}

API
---
"""
import socket
from binascii import crc32
from bz2 import decompress as _bz2_decompress
from re import match as _re_match
from struct import pack as _pack, unpack_from as _unpack_from
from time import time as _time
from enum import IntEnum
from steam.util.binary import StructReader as _StructReader

__all__ = ['query_master', 'a2s_info', 'a2s_players', 'a2s_rules', 'a2s_ping']


def _u(data):
    return data.decode('utf-8', 'replace')


class StructReader(_StructReader):
    def read_cstring(self):
        return _u(super(StructReader, self).read_cstring())


class MSRegion(IntEnum):
    US_East = 0x00
    US_West = 0x01
    South_America = 0x02
    Europe = 0x03
    Asia = 0x04
    Australia = 0x05
    Middle_East = 0x06
    Africa = 0x07
    World = 0xFF


class MSServer:
    GoldSrc = ('hl1master.steampowered.com', 27010)  #: These have been shutdown
    Source = ('hl2master.steampowered.com', 27011)
    Source_27015 = ('208.64.200.65', 27015)          #: ``hl2master`` but on different port


def query_master(filter_text=r'\nappid\500', max_servers=20, region=MSRegion.World, master=MSServer.Source, timeout=2):
    r"""Generator that returns (IP,port) pairs of servers

    .. warning::
        Valve's master servers seem to be heavily rate limited.
        Queries that return a large numbers IPs will timeout before returning everything.
        There is no way to resume the query.
        Use :class:`SteamClient` to access game servers in a reliable way.

    .. note::
        When specifying ``filter_text`` use *raw strings* otherwise python won't treat backslashes
        as literal characters (e.g. ``query(r'\appid\730\white\1')``)

    :param filter_text: filter for servers
    :type  filter_text: str
    :param region: (optional) region code
    :type  region: :class:`.MSRegion`
    :param master: (optional) master server to query
    :type  master: (:class:`str`, :class:`int`)
    :raises: :class:`RuntimeError`, :class:`socket.timeout`
    :returns: a generator yielding (ip, port) pairs
    :rtype: :class:`generator`
    """

    if not isinstance(region, MSRegion):
        raise TypeError("region_code is not of type MSRegion")

    ms = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ms.connect(master)
    ms.settimeout(timeout)

    next_ip = b'0.0.0.0:0'
    req_prefix = b'1' + _pack('>B', region)
    req_suffix = b'\x00' + filter_text.encode('utf-8') + b'\x00'
    n = 0

    while True:
        ms.send(req_prefix + next_ip + req_suffix)

        data = StructReader(ms.recv(8196))  # chunk size needs to be multiple of 6

        # verify response header
        if data.read(6) != b'\xFF\xFF\xFF\xFF\x66\x0A':
            ms.close()
            raise RuntimeError("Invalid response from master server")

        # read list of servers
        while data.rlen():
            ip = '.'.join(map(str, data.unpack('>BBBB')))
            port, = data.unpack('>H')
            n += 1

            # check if we've reached the end of the list
            if ip == '0.0.0.0' and port == 0:
                ms.close()
                return

            yield ip, port

            if n >= max_servers:
                ms.close()
                return

        next_ip = '{}:{}'.format(ip, port).encode('utf-8')

    ms.close()


def _handle_a2s_response(sock):
    packet = sock.recv(2048)
    header, = _unpack_from('<l', packet)

    if header == -1:  # single packet response
        return packet
    elif header == -2:  # multi packet response
        sock.settimeout(0.3)
        return _handle_a2s_multi_packet_response(sock, packet)
    else:
        raise RuntimeError("Invalid reponse header - %d" % header)


def _handle_a2s_multi_packet_response(sock, packet):
    packets, payload_offset = [packet], -1

    # locate first packet and handle out of order packets
    while payload_offset == -1:
        # locate payload offset in uncompressed packet
        payload_offset = packet.find(b'\xff\xff\xff\xff', 0, 18)

        # locate payload offset in compressed packet
        if payload_offset == -1:
            payload_offset = packet.find(b'BZh', 0, 21)

        # if we still haven't found the offset receive the next packet
        if payload_offset == -1:
            packet = sock.recv(2048)
            packets.append(packet)

    # read header
    pkt_idx, num_pkts, compressed = _unpack_multipacket_header(payload_offset, packet)

    if pkt_idx != 0:
        raise RuntimeError("Unexpected first packet index")

    # recv any remaining packets
    while len(packets) < num_pkts:
        packets.append(sock.recv(2048))

    # ensure packets are in correct order
    packets = sorted(map(lambda pkt: (_unpack_multipacket_header(payload_offset, pkt)[0], pkt),
                         packets,
                         ),
                     key=lambda x: x[0])

    # reconstruct full response
    data = b''.join(map(lambda x: x[1][payload_offset:], packets))

    # decompress response if needed
    if compressed:
        size, checksum = _unpack_from('<ll', packet, 10)
        data = _bz2_decompress(data)

        if len(data) != size:
            raise RuntimeError("Response size mismatch - %d %d" % (len(data), size))
        if checksum != crc32(data):
            raise RuntimeError("Response checksum mismatch - %d %d" % (checksum, crc32(data)))

    return data


def _unpack_multipacket_header(payload_offset, packet):
    if payload_offset == 9:  # GoldSrc
        pkt_byte, = _unpack_from('<B', packet, 8)
        return pkt_byte >> 2, pkt_byte & 0xF, False  # idx, total, compressed
    elif payload_offset in (10, 12, 18):  # Source
        pkt_id, num_pkts, pkt_idx, = _unpack_from('<LBB', packet, 4)
        return pkt_idx, num_pkts, (pkt_id & 0x80000000) != 0   # idx, total, compressed
    else:
        raise RuntimeError("Unexpected payload_offset - %d" % payload_offset)


def a2s_info(server_addr, timeout=2, force_goldsrc=False):
    """Get information from a server

    .. note::
        All ``GoldSrc`` games have been updated to reply in ``Source`` format.
        ``GoldSrc`` format is essentially DEPRECATED.
        By default the function will prefer to return ``Source`` format, and will
        automatically fallback to ``GoldSrc`` if available.

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param force_goldsrc: (optional) only accept ``GoldSrc`` response format
    :type  force_goldsrc: :class:`bool`
    :param timeout: (optional) timeout in seconds
    :type  timeout: float
    :raises: :class:`RuntimeError`, :class:`socket.timeout`
    :returns: a dict with information or `None` on timeout
    :rtype: :class:`dict`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    # request server info
    ss.send(_pack('<lc', -1, b'T') + b'Source Engine Query\x00')
    start = _time()

    # handle response(s)
    try:
        data = _handle_a2s_response(ss)
    except:
        ss.close()
        raise

    ping = max(0.0, _time() - start) * 1000

    if force_goldsrc:
        if data[4:5] != b'm':
            ss.close()
            raise socket.timeout('time out')
    else:
        # we got a valid GoldSrc response, check if it is followed by Source response
        if data[4:5] == b'm':
            ss.settimeout(0.3)
            try:
                data = _handle_a2s_response(ss)
            except socket.timeout:
                pass

    ss.close()
    data = StructReader(data)
    header, = data.unpack('<4xc')

    # invalid header
    if header not in b'mI':
        raise RuntimeError("Invalid reponse header - %s" % repr(header))
    # GoldSrc response
    elif header == b'm':
        info = {
            '_ping': ping,
            '_type': 'goldsrc',
            'address': data.read_cstring(),
            'name': data.read_cstring(),
            'map': data.read_cstring(),
            'folder': data.read_cstring(),
            'game': data.read_cstring(),
        }

        (info['players'],
         info['max_players'],
         info['protocol'],
         info['server_type'],
         info['environment'],
         info['visibility'],
         info['mod'],
         ) = data.unpack('<BBBccBB')

        info['server_type'] = _u(info['server_type'])
        info['environment'] = _u(info['environment'])

        if info['mod'] == 1:
            info['link'] = data.read_cstring()
            info['download_link'] = data.read_cstring()

            (info['version'],
             info['size'],
             info['type'],
             info['ddl'],
             ) = data.unpack('<xLLBB')

        info['vac'], info['bots'] = data.unpack('<BB')
    # Source response
    elif header == b'I':
        info = {
            '_ping': ping,
            '_type': 'source',
            'protocol': data.unpack('<b')[0],
            'name': data.read_cstring(),
            'map': data.read_cstring(),
            'folder': data.read_cstring(),
            'game': data.read_cstring(),
        }

        (info['app_id'],
         info['players'],
         info['max_players'],
         info['bots'],
         info['server_type'],
         info['environment'],
         info['visibility'],
         info['vac'],
         ) = data.unpack('<HBBBccBB')

        info['server_type'] = _u(info['server_type'])
        info['environment'] = _u(info['environment'])

        if info['app_id'] == 2400:
            (info['mode'],
             info['witnesses'],
             info['duration'],
             ) = data.unpack('<BBB')

        info['version'] = data.read_cstring()

        if data.rlen():
            edf, = data.unpack('<B')
            info['edf'] = edf

            if edf & 0x80:
                info['port'], = data.unpack('<H')
            if edf & 0x10:
                info['steam_id'], = data.unpack('<Q')
            if edf & 0x40:
                info['sourcetv_port'], = data.unpack('<H')
                info['sourcetv_name'] = data.read_cstring()
            if edf & 0x20:
                info['keywords'] = data.read_cstring()
            if edf & 0x01:
                info['game_id'], = data.unpack('<Q')
                info['app_id'] = info['game_id'] & 0xFFFFFF

    return info


def a2s_players(server_addr, timeout=2, challenge=0):
    """Get list of players and their info

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param timeout: (optional) timeout in seconds
    :type  timeout: float
    :param challenge: (optional) challenge number
    :type  challenge: int
    :raises: :class:`RuntimeError`, :class:`socket.timeout`
    :returns: a list of players
    :rtype: :class:`list`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    # request challenge number
    header = None

    if challenge in (-1, 0):
        ss.send(_pack('<lci', -1, b'U', challenge))
        try:
            data = ss.recv(512)
            _, header, challenge = _unpack_from('<lcl', data)
        except:
            ss.close()
            raise

        if header not in b'AD':  # work around for CSGO sending only max players
            raise RuntimeError("Unexpected challenge response - %s" % repr(header))

    # request player info
    if header == b'D':  # work around for CSGO sending only max players
        data = StructReader(data)
    else:
        ss.send(_pack('<lci', -1, b'U', challenge))

        try:
            data = StructReader(_handle_a2s_response(ss))
        finally:
            ss.close()

    header, num_players = data.unpack('<4xcB')

    if header != b'D':
        raise RuntimeError("Invalid reponse header - %s" % repr(header))

    players = []

    while len(players) < num_players:
        player = dict()
        player['index'] = data.unpack('<B')[0]
        player['name'] = data.read_cstring()
        player['score'], player['duration'] = data.unpack('<lf')
        players.append(player)

    if data.rlen() / 8 == num_players:  # assume the ship server
        for player in players:
            player['deaths'], player['money'] = data.unpack('<ll')

    return players


def a2s_rules(server_addr, timeout=2, challenge=0):
    """Get rules from server

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param timeout: (optional) timeout in seconds
    :type  timeout: float
    :param challenge: (optional) challenge number
    :type  challenge: int
    :raises: :class:`RuntimeError`, :class:`socket.timeout`
    :returns: a list of rules
    :rtype: :class:`list`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    # request challenge number
    if challenge in (-1, 0):
        ss.send(_pack('<lci', -1, b'V', challenge))
        try:
            _, header, challenge = _unpack_from('<lcl', ss.recv(512))
        except:
            ss.close()
            raise

        if header != b'A':
            raise RuntimeError("Unexpected challenge response")

    # request player info
    ss.send(_pack('<lci', -1, b'V', challenge))

    try:
        data = StructReader(_handle_a2s_response(ss))
    finally:
        ss.close()

    header, num_rules = data.unpack('<4xcH')

    if header != b'E':
        raise RuntimeError("Invalid reponse header - %s" % repr(header))

    rules = {}

    while len(rules) != num_rules:
        name = data.read_cstring()
        value = data.read_cstring()

        if _re_match(r'^\-?[0-9]+$', value):
            value = int(value)
        elif _re_match(r'^\-?[0-9]+\.[0-9]+$', value):
            value = float(value)

        rules[name] = value

    return rules


def a2s_ping(server_addr, timeout=2):
    """Ping a server

    .. warning::
        This method for pinging is considered deprecated and may not work on certian servers.
        Use :func:`.a2s_info` instead.

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param timeout: (optional) timeout in seconds
    :type  timeout: float
    :raises: :class:`RuntimeError`, :class:`socket.timeout`
    :returns: ping response in milliseconds or `None` for timeout
    :rtype: :class:`float`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    ss.send(_pack('<lc', -1, b'i'))
    start = _time()

    try:
        data = _handle_a2s_response(ss)
    finally:
        ss.close()

    ping = max(0.0, _time() - start) * 1000

    if data[4:5] == b'j':
        return ping
