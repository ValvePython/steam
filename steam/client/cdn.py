
from collections import OrderedDict, deque
from six import itervalues
import vdf
from steam import webapi
from steam.enums import EServerType
from steam.util.web import make_requests_session
from steam.core.manifest import DepotManifest


def get_content_servers_from_cs(host, port, cell_id, num_servers=20, session=None):
    proto = 'https' if port == 443 else 'http'

    url = '%s://%s:%s/serverlist/%s/%s/' % (proto, host, port, cell_id, num_servers)
    session = make_requests_session() if session is None else session
    resp = session.get(url)

    if resp.status_code != 200:
        return []

    kv = vdf.loads(resp.text, mapper=OrderedDict)

    if kv.get('deferred') == '1':
        return []

    servers = []

    for entry in itervalues(kv['serverlist']):
        server = ContentServer()
        server.type = entry['type']
        server.https = True if entry['https_support'] == 'mandatory' else False
        server.host = entry['Host']
        server.vhost = entry['vhost']
        server.port = 443 if server.https else 80
        server.cell_id = entry['cell']
        server.load = entry['load']
        server.weighted_load = entry['weightedload']
        servers.append(server)

    return servers


def get_content_servers_from_webapi(cell_id, num_servers=20):
    params = {'cellid': cell_id, 'max_servers': num_servers}
    resp = webapi.get('IContentServerDirectoryService', 'GetServersForSteamPipe', params=params)

    servers = []

    for entry in resp['response']['servers']:
        server = ContentServer()
        server.type = entry['type']
        server.https = True if entry['https_support'] == 'mandatory' else False
        server.host = entry['host']
        server.vhost = entry['vhost']
        server.port = 443 if server.https else 80
        server.cell_id = entry.get('cell_id', 0)
        server.load = entry['load']
        server.weighted_load = entry['weighted_load']
        servers.append(server)

    return servers


class CDNClient(object):
    def __init__(self, client, app_id):
        self.steam = client
        self.app_id = app_id
        self.web = make_requests_session()
        self.servers = deque()

    @property
    def cell_id(self):
        return self.steam.cell_id

    def init_servers(self, num_servers=10):
        self.servers.clear()

        for ip, port in self.steam.servers[EServerType.CS]:
            servers = get_content_servers_from_cs(ip, port, self.cell_id, num_servers, self.web)

            if servers:
                self.servers.extend(servers)
                break

        if not self.servers:
            raise RuntimeError("No content servers on SteamClient instance. Is it logged in?")

    def get_content_server(self):
        server = self.servers[0]
        self.servers.rotate(-1)
        return server

    def get(self, command, args, auth_token=''):
        server = self.get_content_server()

        url = "%s://%s:%s/%s/%s%s" % (
            'https' if server.https else 'http',
            server.host,
            server.port,
            command,
            args,
            auth_token,
            )

        return self.web.get(url)

    def get_manifest(self, depot_id, manifest_id, auth_token):
        resp = self.get('depot', '%s/manifest/%s/5' % (depot_id, manifest_id), auth_token)

        resp.raise_for_status()

        if resp.ok:
            return DepotManifest(resp.content)


class ContentServer(object):
    https = False
    host = None
    vhost = None
    port = None
    type = None
    cell_id = 0
    load = None
    weighted_load = None

    def __repr__(self):
        return "<%s('%s://%s:%s', type=%s, cell_id=%s)>" % (
            self.__class__.__name__,
            'https' if self.https else 'http',
            self.host,
            self.port,
            repr(self.type),
            repr(self.cell_id),
            )



