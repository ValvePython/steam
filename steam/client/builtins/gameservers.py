r"""
Listing and information about game servers through Steam

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
from steam.steamid import SteamID
from steam.core.msg import MsgProto
from steam.enums import EResult
from steam.enums.emsg import EMsg
from steam.utils import ip4_to_int, ip4_from_int, ip6_from_bytes
from steam.utils.proto import proto_to_dict
from steam.exceptions import SteamError


class GameServers(object):
    def __init__(self, *args, **kwargs):
        super(GameServers, self).__init__(*args, **kwargs)

        self.gameservers = SteamGameServers(self)  #: instance of :class:`SteamGameServers`


class SteamGameServers(object):
    def __init__(self, steam):
        self._s = steam

    def query(self, filter_text, max_servers=10, timeout=30, **kw):
        r"""
        Query game servers

        https://developer.valvesoftware.com/wiki/Master_Server_Query_Protocol

        .. note::
            When specifying ``filter_text`` use *raw strings* otherwise python won't treat backslashes
            as literal characters (e.g. ``query(r'\appid\730\white\1')``)

        :param filter_text: filter for servers
        :type  filter_text: str
        :param max_servers: (optional) number of servers to return
        :type  max_servers: int
        :param timeout: (optional) timeout for request in seconds
        :type  timeout: int
        :param app_id: (optional) app id
        :type  app_id: int
        :param geo_location_ip: (optional) ip (e.g. '1.2.3.4')
        :type  geo_location_ip: str
        :returns: list of servers, see below. (``None`` is returned steam doesn't respond)
        :rtype: :class:`list`, :class:`None`

        Sample response:

        .. code:: python

            [{'auth_players': 0, 'server_ip': '1.2.3.4', 'query_port': 27015},
             {'auth_players': 6, 'server_ip': '1:2:3:4::5', 'query_port': 27016},
             ...
            ]
        """
        if 'geo_location_ip' in kw:
            kw['geo_location_ip'] = ip4_to_int(kw['geo_location_ip'])

        kw['filter_text'] = filter_text
        kw['max_servers'] = max_servers

        resp = self._s.send_job_and_wait(MsgProto(EMsg.ClientGMSServerQuery),
                                         kw,
                                         timeout=timeout,
                                         )

        if resp is None:
            return None

        resp = proto_to_dict(resp)

        for server in resp['servers']:
            server.pop('deprecated_server_ip', None)  # no point returning this

            if 'v4' in server['server_ip']:
                server['server_ip'] = ip4_from_int(server['server_ip']['v4'])
            else:
                server['server_ip'] = ip6_from_bytes(server['server_ip']['v6'])

        return resp['servers']

    def get_server_list(self, filter_text, max_servers=10, timeout=20):
        """
        Get list of servers. Works similiarly to :meth:`query`, but the response has more details.

        :param filter_text: filter for servers
        :type  filter_text: str
        :param max_servers: (optional) number of servers to return
        :type  max_servers: int
        :param timeout: (optional) timeout for request in seconds
        :type  timeout: int
        :returns: list of servers, see below. (``None`` is returned steam doesn't respond)
        :rtype: :class:`list`, :class:`None`
        :raises: :class:`.SteamError`


        Sample response:

        .. code:: python

            [{'addr': '1.2.3.4:27067',
              'appid': 730,
              'bots': 0,
              'dedicated': True,
              'gamedir': 'csgo',
              'gameport': 27067,
              'gametype': 'valve_ds,empty,secure',
              'map': 'de_dust2',
              'max_players': 10,
              'name': 'Valve CS:GO Asia Server (srcdsXXX.XXX.XXX)',
              'os': 'l',
              'players': 0,
              'product': 'csgo',
              'region': 5,
              'secure': True,
              'steamid': SteamID(id=3279818759, type='AnonGameServer', universe='Public', instance=7011),
              'version': '1.35.4.0'}
            ]
        """
        resp = self._s.send_um_and_wait("GameServers.GetServerList#1",
                                        {
                                         "filter": filter_text,
                                         "limit": max_servers,
                                        },
                                        timeout=20,
                                        )

        if resp is None:
            return None
        if resp.header.eresult != EResult.OK:
            raise SteamError(resp.header.error_message, resp.header.eresult)

        resp = proto_to_dict(resp.body)

        if not resp:
            return []
        else:
            for server in resp['servers']:
                server['steamid'] = SteamID(server['steamid'])

            return resp['servers']

    def get_ips_from_steamids(self, server_steam_ids, timeout=30):
        """Resolve IPs from SteamIDs

        :param server_steam_ids: a list of steamids
        :type  server_steam_ids: list
        :param timeout: (optional) timeout for request in seconds
        :type  timeout: int
        :return: map of ips to steamids
        :rtype: dict
        :raises: :class:`.SteamError`

        Sample response:

        .. code:: python

            {SteamID(id=123456, type='AnonGameServer', universe='Public', instance=1234): '1.2.3.4:27060'}
        """
        resp = self._s.send_um_and_wait("GameServers.GetServerIPsBySteamID#1",
                                        {"server_steamids": server_steam_ids},
                                        timeout=timeout,
                                        )
        if resp is None:
            return None
        if resp.header.eresult != EResult.OK:
            raise SteamError(resp.header.error_message, resp.header.eresult)

        return {SteamID(server.steamid): server.addr for server in resp.body.servers}

    def get_steamids_from_ips(self, server_ips, timeout=30):
        """Resolve SteamIDs from IPs

        :param steam_ids: a list of ips (e.g. ``['1.2.3.4:27015',...]``)
        :type  steam_ids: list
        :param timeout: (optional) timeout for request in seconds
        :type  timeout: int
        :return: map of steamids to ips
        :rtype: dict
        :raises: :class:`.SteamError`

        Sample response:

        .. code:: python

            {'1.2.3.4:27060': SteamID(id=123456, type='AnonGameServer', universe='Public', instance=1234)}
        """
        resp = self._s.send_um_and_wait("GameServers.GetServerSteamIDsByIP#1",
                                        {"server_ips": server_ips},
                                        timeout=timeout,
                                        )
        if resp is None:
            return None
        if resp.header.eresult != EResult.OK:
            raise SteamError(resp.header.error_message, resp.header.eresult)

        return {server.addr: SteamID(server.steamid) for server in resp.body.servers}
