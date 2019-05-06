
from zipfile import ZipFile
from io import BytesIO
from collections import OrderedDict, deque
from six import itervalues, iteritems
from binascii import crc32
from datetime import datetime
import logging
import struct

import vdf
from cachetools import LRUCache
from steam import webapi
from steam.enums import EResult, EServerType
from steam.util.web import make_requests_session
from steam.core.crypto import symmetric_decrypt
from steam.core.manifest import DepotManifest, DepotFile
from steam.protobufs.content_manifest_pb2 import ContentManifestPayload

try:
    import lzma
except ImportError:
    from backports import lzma


def get_content_servers_from_cs(cell_id, host='cs.steamcontent.com', port=80, num_servers=20, session=None):
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


class CDNClient(object):
    _LOG = logging.getLogger("CDNClient")
    servers = deque()
    _chunk_cache = LRUCache(20)

    def __init__(self, client):
        self.steam = client
        self.web = make_requests_session()
        self.cdn_auth_tokens = {}
        self.depot_keys = {}
        self.manifests = {}
        self.app_depots = {}
        self.licensed_app_ids = set()
        self.licensed_depot_ids = set()

        if not self.servers:
            self.fetch_content_servers()

        self.load_licenses()

    def load_licenses(self):
        self.licensed_app_ids.clear()
        self.licensed_depot_ids.clear()

        if not self.steam.licenses:
            self._LOG.debug("No steam licenses available. Is SteamClient instances connected?")
            return

        packages = list(self.steam.licenses.keys())

        print(packages)

        for package_id, info in iteritems(self.steam.get_product_info(packages=packages)['packages']):
            self.licensed_app_ids.update(info['appids'].values())
            self.licensed_depot_ids.update(info['depotids'].values())

    @property
    def cell_id(self):
        return self.steam.cell_id

    def fetch_content_servers(self, num_servers=20):
        self.servers.clear()

        if self.steam:
            for ip, port in self.steam.servers.get(EServerType.CS, []):
                servers = get_content_servers_from_cs(self.cell_id, ip, port, num_servers, self.web)

                if servers:
                    self.servers.extend(servers)
                    break
            else:
                self._LOG.debug("No content servers available on SteamClient instance")

        if not self.servers:
            self._LOG.debug("Trying to fetch content servers from Steam API")

            servers = get_content_servers_from_webapi(self.cell_id)
            self.servers.extend(servers)

        if not self.servers:
            raise ValueError("Failed to fetch content servers")

    def get_content_server(self, rotate=False):
        if rotate:
            self.servers.rotate(-1)
        return self.servers[0]

    def get_cdn_auth_token(self, depot_id):
        if depot_id not in self.cdn_auth_tokens:
            msg = self.steam.get_cdn_auth_token(depot_id, 'steampipe.steamcontent.com')

            if msg and msg.eresult == EResult.OK:
                self.cdn_auth_tokens[depot_id] = msg.token
            else:
                raise ValueError("Failed getting CDN auth token: %s" % repr(
                    EResult.Timeout if msg is None else EResult(msg.eresult)))

        return self.cdn_auth_tokens[depot_id]

    def get_depot_key(self, app_id, depot_id):
        if (app_id, depot_id) not in self.depot_keys:
            msg = self.steam.get_depot_key(app_id, depot_id)

            if msg and msg.eresult == EResult.OK:
                self.depot_keys[(app_id, depot_id)] = msg.depot_encryption_key
            else:
                raise ValueError("Failed getting depot key: %s" % repr(
                    EResult.Timeout if msg is None else EResult(msg.eresult)))

        return self.depot_keys[(app_id, depot_id)]

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

            try:
                resp = self.web.get(url)
            except:
                pass
            else:
                if resp.ok:
                    return resp
                elif resp.status_code in (401, 403, 404):
                    resp.raise_for_status()

            server = self.get_content_server(rotate=True)

    def get_chunk(self, app_id, depot_id, chunk_id, cdn_auth_token=None):
        if (depot_id, chunk_id) not in self._chunk_cache:
            if cdn_auth_token is None:
                cdn_auth_token = self.get_cdn_auth_token(depot_id)

            resp = self.get('depot', '%s/chunk/%s' % (depot_id, chunk_id), cdn_auth_token)

            data = symmetric_decrypt(resp.content, self.get_depot_key(app_id, depot_id))

            if data[:2] == b'VZ':
                if data[2:3] != b'a':
                    raise ValueError("Invalid VZ version: %s" % repr(data[2:3]))

                vzfilter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, data[7:12])
                vzdec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[vzfilter])
                checksum, decompressed_size, vz_footer = struct.unpack('<II2s', data[-10:])
                # i have no idea why, but some chunks will decompress with 1 extra byte at the end
                udata = vzdec.decompress(data[12:-10])[:decompressed_size]

                if vz_footer != b'zv':
                    raise ValueError("Invalid VZ footer: %s" % repr(vz_footer))
                if crc32(udata) != checksum:
                    raise ValueError("CRC checksum doesn't match for decompressed data")

                data = udata[:decompressed_size]

            else:
                with ZipFile(BytesIO(data)) as zf:
                    data = zf.read(zf.filelist[0])

            self._chunk_cache[(depot_id, chunk_id)] = data

        return self._chunk_cache[(depot_id, chunk_id)]

    def get_manifest(self, app_id, depot_id, manifest_id, cdn_auth_token=None, decrypt=True):
        if (app_id, depot_id, manifest_id) not in self.manifests:
            if cdn_auth_token is None:
                cdn_auth_token = self.get_cdn_auth_token(depot_id)

            resp = self.get('depot', '%s/manifest/%s/5' % (depot_id, manifest_id), cdn_auth_token)

            if resp.ok:
                manifest = CDNDepotManifest(self, app_id, resp.content)
                if decrypt:
                    manifest.decrypt_filenames(self.get_depot_key(app_id, depot_id))
                self.manifests[(app_id, depot_id, manifest_id)] = manifest

        return self.manifests[(app_id, depot_id, manifest_id)]

    def get_manifests(self, app_id, branch='public', filter_func=None):
        if app_id not in self.app_depots:
            self.app_depots[app_id] = self.steam.get_product_info([app_id])['apps'][app_id]['depots']
        depots = self.app_depots[app_id]

        if branch not in depots['branches']:
            raise ValueError("No branch named %s for app_id %s" % (repr(branch), app_id))
        elif int(depots['branches'][branch].get('pwdrequired', 0)) > 0:
            raise NotImplementedError("Password protected branches are not supported yet")

        manifests = []

        for depot_id, depot_info in iteritems(depots):
            if not depot_id.isdigit():
                continue

            depot_id = int(depot_id)

            # if we have no license for the depot, no point trying as we won't get depot_key
            if depot_id not in self.licensed_depot_ids:
                self._LOG.debug("No license for depot %s (%s). Skipping...",
                                repr(depot_info['name']),
                                depot_id,
                                )
                continue

            # if filter_func set, use it to filter the list the depots
            if filter_func and not filter_func(depot_id, depot_info):
                continue

            # get manifests for the sharedinstalls
            if depot_info.get('sharedinstall') == '1':
                manifests += self.get_manifests(int(depot_info['depotfromapp']),
                                                filter_func=(lambda a, b: int(a) == depot_id),
                                                )
                continue

            # process depot, and get manifest for branch
            if branch in depot_info.get('manifests', {}):
                try:
                    manifest = self.get_manifest(app_id, depot_id, depot_info['manifests'][branch])
                except ValueError as exp:
                    self._LOG.error("Depot %s (%s): %s",
                                    repr(depot_info['name']),
                                    depot_id,
                                    str(exp),
                                    )
                    continue

                manifest.name = depot_info['name']
                manifests.append(manifest)

        return manifests

    def iter_files(self, app_id, filename_filter=None, branch='public', filter_func=None):
        for manifest in self.get_manifests(app_id, branch, filter_func):
            for fp in manifest.iter_files(filename_filter):
                yield fp

    def get_manifest_for_workshop_item(self, item_id):
        resp, error = self.steam.unified_messages.send_and_wait('PublishedFile.GetDetails#1', {
            'publishedfileids': [item_id],
            'includetags': False,
            'includeadditionalpreviews': False,
            'includechildren': False,
            'includekvtags': False,
            'includevotes': False,
            'short_description': True,
            'includeforsaledata': False,
            'includemetadata': False,
            'language': 0
        }, timeout=7)

        if error:
            raise error

        wf = None if resp is None else resp.publishedfiledetails[0]

        if wf is None or wf.result != EResult.OK:
            raise ValueError("Failed getting workshop file info: %s" % repr(
                EResult.Timeout if resp is None else EResult(wf.result)))
        elif not wf.hcontent_file:
            raise ValueError("Workshop file is not on steampipe")

        app_id = ws_app_id = wf.consumer_appid

        manifest = self.get_manifest(app_id, ws_app_id, wf.hcontent_file)
        manifest.name = wf.title
        return manifest


class CDNDepotManifest(DepotManifest):
    name = None  #: set only by :meth:`CDNClient.get_manifests`

    def __init__(self, cdn_client, app_id, data):
        self.cdn_client = cdn_client
        self.app_id = app_id
        DepotManifest.__init__(self, data)

    def __repr__(self):
        params = ', '.join([
                    "app_id=" + str(self.app_id),
                    "depot_id=" + str(self.depot_id),
                    "gid=" + str(self.gid),
                    "creation_time=" + repr(
                        datetime.utcfromtimestamp(self.metadata.creation_time).isoformat().replace('T', ' ')
                        ),
                    ])

        if self.name:
            params = repr(self.name) + ', ' + params

        if self.metadata.filenames_encrypted:
            params += ', filenames_encrypted=True'

        return "<%s(%s)>" % (
            self.__class__.__name__,
            params,
            )

    def deserialize(self, data):
        DepotManifest.deserialize(self, data)

        # order chunks in ascending order by their offset
        # required for CDNDepotFile
        for mapping in self.payload.mappings:
            mapping.chunks.sort(key=lambda x: x.offset)

    def _make_depot_file(self, file_mapping):
        return CDNDepotFile(self, file_mapping)


class CDNDepotFile(DepotFile):
    def __init__(self, manifest, file_mapping):
        if not isinstance(manifest, CDNDepotManifest):
            raise TypeError("Expected 'manifest' to be of type CDNDepotFile")
        if not isinstance(file_mapping, ContentManifestPayload.FileMapping):
            raise TypeError("Expected 'file_mapping' to be of type ContentManifestPayload.FileMapping")

        DepotFile.__init__(self, manifest, file_mapping)

        self.offset = 0
        self._lc = None
        self._lcbuff = b''

    def __repr__(self):
        return "<%s(%s, %s, %s, %s, %s)>" % (
            self.__class__.__name__,
            self.manifest.app_id,
            self.manifest.depot_id,
            self.manifest.gid,
            repr(self.filename),
            'is_directory=True' if self.is_directory else self.size,
            )

    @property
    def name(self):
        return self.filename

    @property
    def seekable(self):
        return self.is_file

    def tell(self):
        if not self.seekable:
            raise ValueError("This file is not seekable, probably because its directory or symlink")
        return self.offset

    def seek(self, offset, whence=0):
        if not self.seekable:
            raise ValueError("This file is not seekable, probably because its directory or symlink")

        if whence == 0:
            if offset < 0:
                raise IOError("Invalid argument")
        elif whence == 1:
            offset = self.offset + offset
        elif whence == 2:
            offset = self.size + offset
        else:
            raise ValueError("Invalid value for whence")

        self.offset = max(0, min(self.size, offset))

    def _get_chunk(self, chunk):
        if not self._lc or self._lc.sha != chunk.sha:
            self._lcbuff = self.manifest.cdn_client.get_chunk(
                self.manifest.app_id,
                self.manifest.depot_id,
                chunk.sha.hex(),
                )
            self._lc = chunk
        return self._lcbuff

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def next(self):
        line = self.readline()
        if line == b'':
            raise StopIteration
        return line

    def read(self, length=-1):
        if length == -1:
            length = self.size - self.offset
        if length == 0 or self.offset >= self.size or self.size == 0:
            return b''

        end_offset = self.offset + length

        # we cache last chunk to allow small length reads and local seek
        if (self._lc
           and self.offset >= self._lc.offset
           and end_offset <= self._lc.offset + self._lc.cb_original):
            data = self._lcbuff[self.offset - self._lc.offset:self.offset - self._lc.offset + length]
        # if we need to read outside the bounds of the cached chunk
        # we go to loop over chunks to determine which to download
        else:
            data = BytesIO()
            start_offset = None

            # Manifest orders the chunks in ascending order by offset
            for chunk in self.chunks:
                if chunk.offset >= end_offset:
                    break
                elif (chunk.offset <= self.offset < chunk.offset + chunk.cb_original
                      or chunk.offset < end_offset <= chunk.offset + chunk.cb_original):
                    if start_offset is None:
                        start_offset = chunk.offset
                    data.write(self._get_chunk(chunk))

            data.seek(self.offset - start_offset)
            data = data.read(length)

        self.offset = min(self.size, end_offset)
        return data

    def readline(self):
        buf = b''

        for chunk in iter(lambda: self.read(256), b''):
            pos = chunk.find(b'\n')
            if pos > -1:
                pos += 1  # include \n
                buf += chunk[:pos]
                self.seek(self.offset - (len(chunk) - pos))
                break

            buf += chunk

        return buf

    def readlines(self):
        return [line for line in self]
