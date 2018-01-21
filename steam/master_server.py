r""" Master Server Query Protocol

This module implements the legacy Steam master server protocol.

https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol

Nowadays games query servers through Steam. See :any:`steam.client.builtins.gameservers`

Filters
-------

.. note::
    Multiple filters can be joined to together (Eg. ``\app\730\white\1\empty\1``)

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
"""
import socket
from struct import pack as _pack, unpack_from as _unpack_from
from time import time as _time
from enum import IntEnum, Enum
from steam.util.binary import StructReader


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


def query(filter_text=r'\napp\500', region=MSRegion.World, master=MSServer.Source):
    r"""Generator that returns (IP,port) pairs of serveras

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
    :raises: This function will raise in various situations
    :returns: a generator yielding (ip, port) pairs
    :rtype: :class:`generator`
    """

    if not isinstance(region, MSRegion):
        raise TypeError("region_code is not of type MSRegion")

    ms = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ms.connect(master)
    ms.settimeout(8)

    next_ip = b'0.0.0.0:0'
    req_prefix = b'1' + _pack('>B', region)
    req_suffix = b'\x00' + filter_text.encode('utf-8') + b'\x00'

    while True:
        ms.send(req_prefix + next_ip + req_suffix)

        data = ms.recv(2048)
        data = StructReader(data)

        # verify response header
        if data.read(6) != b'\xFF\xFF\xFF\xFF\x66\x0A':
            raise RuntimeError("Invalid response from master server")

        # read list of servers
        while data.rlen():
            ip = '.'.join(map(str, data.unpack('>BBBB')))
            port, = data.unpack('>H')

            # check if we've reach the end of the list
            if ip == '0.0.0.0' and port == 0:
                return

            yield ip, port

        next_ip = '{}:{}'.format(ip, port).encode('utf-8')


def _handle_a2s_response(sock):
    packet = sock.recv(2048)
    header, = _unpack_from('<l', packet)

    if header == -1:  # single packet response
        return packet[4:]
    elif header == -2:  # multi packet response
        raise RuntimeError("Multi packet response not implemented yet")
    else:
        raise RuntimeError("Invalid reponse header")


def a2s_info(server_addr, goldsrc=False, timeout=6):
    """Get information from a server

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param goldsrc: (optional) Weather to expect GoldSrc or Source response format
    :type  goldsrc: :class:`bool`
    :param timeout: (optional) timeout in seconds
    :type  timeout: int
    :returns: a dict with information or `None` on timeout
    :rtype: :class:`dict`, :class:`None`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    # request server info
    ss.send(_pack('<lc', -1, b'T') + b'Source Engine Query\x00')
    resp_header = b'm' if goldsrc else b'I'

    while True:
        try:
            data = _handle_a2s_response(ss)
        except socket.timeout:
            return None
        else:
            if data[0:1] == resp_header:
                break

    data = StructReader(data)
    data.skip(1)  # header

    # GoldSrc response
    if goldsrc:
        info = {
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

        if info['mod'] == 1:
            info['link'] = data.read_cstring(),
            info['download_link'] = data.read_cstring(),

            (info['version'],
             info['size'],
             info['type'],
             info['ddl'],
             ) = data.unpack('<xLLBB')

        info['vac'], info['bots'] = data.unpack('<BB')
    # Source response
    else:
        info = {
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

    return info


def a2s_player(server_addr, challenge=0, timeout=8):
    """Get list of players and their info

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param challenge: (optional) challenge number
    :type  challenge: int
    :param timeout: (optional) timeout in seconds
    :type  timeout: int
    :returns: a list of players
    :rtype: :class:`list`, :class:`None`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    # request challenge number
    if challenge in (-1, 0):
        ss.send(_pack('<lci', -1, b'U', challenge))
        _, header, challange = _unpack_from('<lcl', ss.recv(512))

        if header != b'A':
            raise RuntimeError("Unexpected challange response")

    # request player info
    ss.send(_pack('<lci', -1, b'U', challange))

    try:
        data = StructReader(_handle_a2s_response(ss))
    except socket.timeout:
        return None

    header, num_players = data.unpack('<BB')

    players = []

    while len(players) != num_players:
        player = dict()
        player['index'] = data.unpack('<B')[0]
        player['name'] = data.read_cstring()
        player['score'], player['duration'] = data.unpack('<lf')
        players.append(player)

    if data.rlen() / 8 == num_players:  # assume the ship server
        for player in players:
            player['deaths'], player['money'] = data.unpack('<ll')

    return players


def a2s_ping(server_addr, timeout=8):
    """Ping a server

    .. warning::
        This method for pinging is considered deprecated and will not work on newer sources games

    :param server_addr: (ip, port) for the server
    :type  server_addr: tuple
    :param timeout: (optional) timeout in seconds
    :type  timeout: int
    :returns: ping response in seconds or `None` for timeout
    :rtype: :class:`float`, :class:`None`
    """
    ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ss.connect(server_addr)
    ss.settimeout(timeout)

    ss.send(_pack('<lc', -1, b'i'))
    start = _time()

    try:
        data = _handle_a2s_response(ss)
    except socket.timeout:
        return None

    diff = _time() - start

    if data[0:1] == b'j':
        return diff
