
from zipfile import ZipFile
from io import BytesIO
from collections import OrderedDict, deque
from six import itervalues
import vdf

from steam import webapi
from steam.enums import EResult, EServerType
from steam.util.web import make_requests_session
from steam.core.crypto import symmetric_decrypt
from steam.core.manifest import DepotManifest

try:
    import lzma
except ImportError:
    from backports import lzma


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
        self.cdn_auth_tokens = {}
        self.depot_keys = {}

    @property
    def cell_id(self):
        return self.steam.cell_id

    def init_servers(self, num_servers=20):
        self.servers.clear()

        for ip, port in self.steam.servers[EServerType.CS]:
            servers = get_content_servers_from_cs(ip, port, self.cell_id, num_servers, self.web)

            if servers:
                self.servers.extend(servers)
                break

        if not self.servers:
            raise RuntimeError("No content servers on SteamClient instance. Is it logged in?")

    def get_content_server(self, rotate=True):
        if rotate:
            self.servers.rotate(-1)
        return self.servers[0]

    def get_cdn_auth_token(self, depot_id):
        if depot_id not in self.cdn_auth_tokens:
            msg = self.steam.get_cdn_auth_token(depot_id, 'steampipe.steamcontent.com')

            if msg.eresult == EResult.OK:
                self.cdn_auth_tokens[depot_id] = msg.token
            elif msg is None:
                raise Exception("Failed getting depot key: %s" % repr(EResult.Timeout))
            else:
                raise Exception("Failed getting depot key: %s" % repr(EResult(msg.eresult)))

        return self.cdn_auth_tokens[depot_id]

    def get_depot_key(self, depot_id):
        if depot_id not in self.depot_keys:
            msg = self.steam.get_depot_key(self.app_id, depot_id)
            if msg.eresult == EResult.OK:
                self.depot_keys[depot_id] = msg.depot_encryption_key
            elif msg is None:
                raise Exception("Failed getting depot key: %s" % repr(EResult.Timeout))
            else:
                raise Exception("Failed getting depot key: %s" % repr(EResult(msg.eresult)))

        return self.depot_keys[depot_id]

    def get(self, command, args, auth_token=''):
        server = self.get_content_server()

        while True:
            url = "%s://%s:%s/%s/%s%s" % (
                'https' if server.https else 'http',
                server.host,
                server.port,
                command,
                args,
                auth_token,
                )
            resp = self.web.get(url)

            if resp.ok:
                return resp
            elif resp.status_code in (401, 403, 404):
                resp.raise_for_status()

            server = self.get_content_server(rotate=True)

    def get_manifest(self, depot_id, manifest_id, cdn_auth_token=None, decrypt=True):
        if cdn_auth_token is None:
            cdn_auth_token = self.get_cdn_auth_token(depot_id)

        resp = self.get('depot', '%s/manifest/%s/5' % (depot_id, manifest_id), cdn_auth_token)

        if resp.ok:
            manifest = DepotManifest(resp.content)
            if decrypt:
                manifest.decrypt_filenames(self.get_depot_key(depot_id))
            return manifest

    def get_chunk(self, depot_id, chunk_id, cdn_auth_token=None):
        if cdn_auth_token is None:
            cdn_auth_token = self.get_cdn_auth_token(depot_id)

        resp = self.get('depot', '%s/chunk/%s' % (depot_id, chunk_id), cdn_auth_token)

        if resp.ok:
            data = symmetric_decrypt(resp.content, self.get_depot_key(depot_id))

            if data[:3] == b'VZa':
                f = lzma._decode_filter_properties(lzma.FILTER_LZMA1, data[7:12])
                return lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[f]).decompress(data[12:-10])
            else:
                with ZipFile(BytesIO(data)) as zf:
                    return zf.read(zf.filelist[0])


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
