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
import struct
from time import sleep
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
    req_prefix = b'1' + struct.pack('>B', region)
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
                raise StopIteration

            yield ip, port

        next_ip = '{}:{}'.format(ip, port).encode('utf-8')
