"""
The :class:`.CDNClient` class provides a simple API for downloading Steam content from SteamPipe

Initializing :class:`.CDNClient` requires a logged in :class:`.SteamClient` instance

.. warning::
    This module uses :mod:`requests` library, which is not gevent cooperative by default.
    It is high recommended that you use :meth:`steam.monkey.patch_minimal()`.
    See example below

.. code:: python
    import steam.monkey
    steam.monkey.patch_minimal()

    from steam.client import SteamClient, EMsg
    from steam.client.cdn import CDNClient

    mysteam = SteamClient()
    mysteam.cli_login()
    ...
    mycdn = CDNClient(mysteam)


Getting depot manifests for an app

.. code:: python

    >>> mycdn.get_manifests(570)
    [<CDNDepotManifest('Dota 2 Content', app_id=570, depot_id=373301, gid=6397590570861788404, creation_time='2019-06-29 16:03:11')>,
     <CDNDepotManifest('Dota 2 Content 2', app_id=570, depot_id=381451, gid=5769691971272474272, creation_time='2019-06-29 00:19:02')>,
     <CDNDepotManifest('Dota 2 Content 3', app_id=570, depot_id=381452, gid=3194393866044592918, creation_time='2019-06-27 00:05:38')>,
     <CDNDepotManifest('Dota 2 Content 4', app_id=570, depot_id=381453, gid=8005824150061180163, creation_time='2019-06-08 07:49:57')>,
     <CDNDepotManifest('Dota 2 Content 5', app_id=570, depot_id=381454, gid=9003299908441378336, creation_time='2019-06-26 18:56:19')>,
     <CDNDepotManifest('Dota 2 Content 6', app_id=570, depot_id=381455, gid=8000458746487720619, creation_time='2019-06-29 00:19:43')>,
     <CDNDepotManifest('Dota 2 Win32', app_id=570, depot_id=373302, gid=3561463682334619841, creation_time='2019-06-29 00:16:28')>,
     <CDNDepotManifest('Dota 2 Win64', app_id=570, depot_id=373303, gid=6464064782313084040, creation_time='2019-06-29 00:16:43')>,
     <CDNDepotManifest('Dota 2 Mac', app_id=570, depot_id=373304, gid=5979018571482579541, creation_time='2019-06-29 00:16:59')>,
     <CDNDepotManifest('Dota 2 English', app_id=570, depot_id=373305, gid=4435851250675935801, creation_time='2015-06-01 20:15:37')>,
     <CDNDepotManifest('Dota 2 Linux', app_id=570, depot_id=373306, gid=4859464855297921815, creation_time='2019-06-29 00:17:25')>,
     <CDNDepotManifest('Dota 2 Korean', app_id=570, depot_id=373308, gid=8598853793233320583, creation_time='2019-03-05 17:16:49')>,
     <CDNDepotManifest('Dota 2 Simplified Chinese', app_id=570, depot_id=373309, gid=6975893321745168138, creation_time='2019-06-25 21:40:37')>,
     <CDNDepotManifest('Dota 2 Russian', app_id=570, depot_id=381456, gid=5425063725991897591, creation_time='2019-03-05 17:19:53')>,
     <CDNDepotManifest('Dota 2 Workshop tools', app_id=570, depot_id=381450, gid=8629205096668418087, creation_time='2019-06-29 16:04:18')>,
     <CDNDepotManifest('Dota 2 OpenGL Windows', app_id=570, depot_id=401531, gid=6502316736107281444, creation_time='2019-06-07 19:04:08')>,
     <CDNDepotManifest('Dota 2 Vulkan Common', app_id=570, depot_id=401535, gid=6405492872419215600, creation_time='2019-06-07 19:04:11')>,
     <CDNDepotManifest('Dota 2 Vulkan Win64', app_id=570, depot_id=401536, gid=3821288251412129608, creation_time='2019-06-25 21:42:29')>,
     <CDNDepotManifest('Dota 2 Vulkan Linux64', app_id=570, depot_id=401537, gid=3144805829218032316, creation_time='2019-06-17 16:54:43')>,
     <CDNDepotManifest('Dota 2 VR', app_id=570, depot_id=313255, gid=706332602567268673, creation_time='2017-10-04 18:52:14')>,
     <CDNDepotManifest('Dota 2 Vulkan Mac', app_id=570, depot_id=401538, gid=2223235822414824351, creation_time='2019-06-11 19:37:19')>]

    >>> mycdn.get_manifests(570, filter_func=lambda depot_id, info: 'Dota 2 Content' in info['name'])
    [<CDNDepotManifest('Dota 2 Content', app_id=570, depot_id=373301, gid=6397590570861788404, creation_time='2019-06-29 16:03:11')>,
     <CDNDepotManifest('Dota 2 Content 2', app_id=570, depot_id=381451, gid=5769691971272474272, creation_time='2019-06-29 00:19:02')>,
     <CDNDepotManifest('Dota 2 Content 3', app_id=570, depot_id=381452, gid=3194393866044592918, creation_time='2019-06-27 00:05:38')>,
     <CDNDepotManifest('Dota 2 Content 4', app_id=570, depot_id=381453, gid=8005824150061180163, creation_time='2019-06-08 07:49:57')>,
     <CDNDepotManifest('Dota 2 Content 5', app_id=570, depot_id=381454, gid=9003299908441378336, creation_time='2019-06-26 18:56:19')>,
     <CDNDepotManifest('Dota 2 Content 6', app_id=570, depot_id=381455, gid=8000458746487720619, creation_time='2019-06-29 00:19:43')>]


Listing files

.. code:: python

    >>> file_list = mycdn.iter_files(570)
    >>> list(file_list)[:10]
    [<CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\dungeon\\particles\\test_particle\\generic_attack_crit_blur_rope.vpcf_c', 2134)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\dungeon\\materials\\blends\\mud_brick_normal_psd_5cc4fe8b.vtex_c', 351444)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\hero_demo\\scripts\\vscripts\\la_spawn_enemy_at_target.lua', 1230)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\winter_2018\\particles\\dark_moon\\darkmoon_last_hit_effect_damage_flash_b.vpcf_c', 1386)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\dungeon\\scripts\\vscripts\\abilities\\siltbreaker_line_wave.lua', 3305)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\dungeon\\materials\\models\\heroes\\broodmother\\broodmother_body_poison.vmat_c', 10888)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota\\resource\\cursor\\workshop\\sltv_shaker_cursor_pack\\cursor_spell_default.ani', 4362)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\overthrow\\panorama\\images\\custom_game\\team_icons\\team_icon_tiger_01_png.vtex_c', 18340)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota\\resource\\cursor\\valve\\ti7\\cursor_attack_illegal.bmp', 4152)>,
     <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota_addons\\winter_2018\\models\\creeps\\ice_biome\\undeadtusk\\undead_tuskskeleton01.vmdl_c', 13516)>

Reading a file directly from SteamPipe

.. code:: python

    >>> file_list = mycdn.iter_files(570, r'game\dota\gameinfo.gi')
    >>> myfile = next(file_list)
    <CDNDepotFile(570, 373301, 6397590570861788404, 'game\\dota\\gameinfo.gi', 6808)>
    >>> print(myfile.read(80).decode('utf-8'))
    "GameInfo"
    {
            game            "Dota 2"
            title           "Dota 2"

            gamelogo 1
            type            multiplayer_only
    ...

"""

from zipfile import ZipFile
from io import BytesIO
from collections import OrderedDict, deque
from six import itervalues, iteritems
from binascii import crc32, unhexlify
from datetime import datetime
import logging
import struct

import vdf
from gevent.pool import Pool as GPool
from cachetools import LRUCache
from steam import webapi
from steam.exceptions import SteamError, ManifestError
from steam.core.msg import MsgProto
from steam.enums import EResult, EType
from steam.enums.emsg import EMsg
from steam.utils.web import make_requests_session
from steam.core.crypto import symmetric_decrypt, symmetric_decrypt_ecb
from steam.core.manifest import DepotManifest, DepotFile
from steam.protobufs.content_manifest_pb2 import ContentManifestPayload

try:
    import lzma
except ImportError:
    from backports import lzma

def decrypt_manifest_gid_2(encrypted_gid, password):
    """Decrypt manifest gid v2 bytes

    :param encrypted_gid: encrypted gid v2 bytes
    :type  encrypted_gid: bytes
    :param password: encryption password
    :type  password: byt
    :return: manifest gid
    :rtype: int
    """
    return struct.unpack('<Q', symmetric_decrypt_ecb(encrypted_gid, password))[0]

def get_content_servers_from_cs(cell_id, host='cs.steamcontent.com', port=80, num_servers=20, session=None):
    """Get a list of CS servers from a single CS server

    :param cell_id: location cell id
    :type  cell_id: bytes
    :param host: CS server host
    :type  host: str
    :param port: server port number
    :type  port: int
    :param num_servers: number of servers to return
    :type  num_servers: int
    :param session: requests Session instance
    :type  session: :class:`requests.Session`
    :return: list of CS servers
    :rtype: :class:`list` [:class:`.ContentServer`]
    """
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
    """Get a list of CS servers from Steam WebAPI

    :param cell_id: location cell id
    :type  cell_id: bytes
    :param num_servers: number of servers to return
    :type  num_servers: int
    :return: list of CS servers
    :rtype: :class:`list` [:class:`.ContentServer`]
    """
    params = {'cell_id': cell_id, 'max_servers': num_servers}
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


class CDNDepotFile(DepotFile):
    def __init__(self, manifest, file_mapping):
        """File-like object proxy for content files located on SteamPipe

        :param manifest: parrent manifest instance
        :type  manifest: :class:`.CDNDepotManifest`
        :param file_mapping: file mapping instance from manifest
        :type  file_mapping: ContentManifestPayload.FileMapping
        """
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
            repr(self.filename_raw),
            'is_directory=True' if self.is_directory else self.size,
            )

    @property
    def seekable(self):
        """:type: bool"""
        return self.is_file

    def tell(self):
        """:type: int"""
        if not self.seekable:
            raise ValueError("This file is not seekable, probably because its directory or symlink")
        return self.offset

    def seek(self, offset, whence=0):
        """Seen file

        :param offset: file offset
        :type  offset: int
        :param whence: offset mode, see :meth:`io.IOBase.seek`
        :type  whence: int
        """
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
        """Read bytes from the file

        :param length: number of bytes to read. Read the whole file if not set
        :type  length: int
        :returns: file data
        :rtype: bytes
        """
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

            # Manifest orders the chunks by offset in ascending order
            for chunk in self.chunks:
                if chunk.offset >= end_offset:
                    break

                chunk_start = chunk.offset
                chunk_end = chunk_start + chunk.cb_original

                if (     chunk_start <= self.offset <  chunk_end
                      or (chunk_start > self.offset and end_offset > chunk_end)
                      or chunk_start <  end_offset  <= chunk_end):
                    if start_offset is None:
                        start_offset = chunk.offset
                    data.write(self._get_chunk(chunk))

            data.seek(self.offset - start_offset)
            data = data.read(length)

        self.offset = min(self.size, end_offset)
        return data

    def readline(self):
        """Read a single line

        :return: single file line
        :rtype: bytes
        """
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
        """Get file contents as list of lines

        :return: list of lines
        :rtype: :class:`list` [:class:`bytes`]
        """
        return [line for line in self]


class CDNDepotManifest(DepotManifest):
    DepotFileClass = CDNDepotFile
    name = None  #: set only by :meth:`CDNClient.get_manifests`

    def __init__(self, cdn_client, app_id, data):
        """Holds manifest metadata and file list.

        :param cdn_client: CDNClient instance
        :type  cdn_client: :class:`.CDNClient`
        :param app_id: App ID
        :type  app_id: int
        :param data: serialized manifest data
        :type  data: bytes
        """
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

        if self.filenames_encrypted:
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
            mapping.chunks.sort(key=lambda x: x.offset, reverse=False)


class CDNClient(object):
    DepotManifestClass = CDNDepotManifest
    _LOG = logging.getLogger("CDNClient")
    servers = deque()  #: CS Server list
    _chunk_cache = LRUCache(20)
    cell_id = 0  #: Cell ID to use, initialized from SteamClient instance

    def __init__(self, client):
        """CDNClient allows loading and reading of manifests for Steam apps are used
        to list and download content

        :param client: logged in SteamClient instance
        :type  client: :class:`.SteamClient`
        """
        self.gpool = GPool(8)            #: task pool
        self.steam = client              #: SteamClient instance
        if self.steam:
            self.cell_id = self.steam.cell_id

        self.web = make_requests_session()
        self.depot_keys = {}             #: depot decryption keys
        self.manifests = {}              #: CDNDepotManifest instances
        self.app_depots = {}             #: app depot info
        self.beta_passwords = {}         #: beta branch decryption keys
        self.licensed_app_ids = set()    #: app_ids that the SteamClient instance has access to
        self.licensed_depot_ids = set()  #: depot_ids that the SteamClient instance has access to

        if not self.servers:
            self.fetch_content_servers()

        self.load_licenses()

    def clear_cache(self):
        """Cleared cached information. Next call on methods with caching will return fresh data"""
        self.manifests.clear()
        self.app_depots.clear()
        self.beta_passwords.clear()

    def load_licenses(self):
        """Read licenses from SteamClient instance, required for determining accessible content"""
        self.licensed_app_ids.clear()
        self.licensed_depot_ids.clear()

        if self.steam.steam_id.type == EType.AnonUser:
            packages = [17906]
        else:
            if not self.steam.licenses:
                self._LOG.debug("No steam licenses found on SteamClient instance")
                return

            packages = list(map(lambda l: {'packageid': l.package_id, 'access_token': l.access_token},
                                itervalues(self.steam.licenses)))

        for package_id, info in iteritems(self.steam.get_product_info(packages=packages)['packages']):
            self.licensed_app_ids.update(info['appids'].values())
            self.licensed_depot_ids.update(info['depotids'].values())

    def fetch_content_servers(self, num_servers=20):
        """Update CS server list

        :param num_servers: numbers of CS server to fetch
        :type  num_servers: int
        """
        self.servers.clear()

        self._LOG.debug("Trying to fetch content servers from Steam API")

        servers = get_content_servers_from_webapi(self.cell_id)
        servers = filter(lambda server: server.type != 'OpenCache', servers) # see #264
        self.servers.extend(servers)

        if not self.servers:
            raise SteamError("Failed to fetch content servers")

    def get_content_server(self, rotate=False):
        """Get a CS server for content download

        :param rotate: forcefully rotate server list and get a new server
        :type  rotate: bool
        """
        if rotate:
            self.servers.rotate(-1)
        return self.servers[0]

    def get_depot_key(self, app_id, depot_id):
        """Get depot key, which is needed to decrypt files

        :param app_id: app id
        :type  app_id: int
        :param depot_id: depot id
        :type  depot_id: int
        :return: returns decryption key
        :rtype: bytes
        :raises SteamError: error message
        """
        if depot_id not in self.depot_keys:
            msg = self.steam.get_depot_key(app_id, depot_id)

            if msg and msg.eresult == EResult.OK:
                self.depot_keys[depot_id] = msg.depot_encryption_key
            else:
                raise SteamError("Failed getting depot key",
                                 EResult.Timeout if msg is None else EResult(msg.eresult))

        return self.depot_keys[depot_id]

    def cdn_cmd(self, command, args):
        """Run CDN command request

        :param command: command name
        :type  command: str
        :param args: args
        :type  args: str
        :returns: requests response
        :rtype: :class:`requests.Response`
        :raises SteamError: on error
        """
        server = self.get_content_server()

        while True:
            url = "%s://%s:%s/%s/%s" % (
                'https' if server.https else 'http',
                server.host,
                server.port,
                command,
                args,
                )

            try:
                resp = self.web.get(url, timeout=10)
            except Exception as exp:
                self._LOG.debug("Request error: %s", exp)
            else:
                if resp.ok:
                    return resp
                elif 400 <= resp.status_code < 500:
                    self._LOG.debug("Got HTTP %s", resp.status_code)
                    raise SteamError("HTTP Error %s" % resp.status_code)
                self.steam.sleep(0.5)

            server = self.get_content_server(rotate=True)

    def get_chunk(self, app_id, depot_id, chunk_id):
        """Download a single content chunk

        :param app_id: App ID
        :type  app_id: int
        :param depot_id: Depot ID
        :type  depot_id: int
        :param chunk_id: Chunk ID
        :type  chunk_id: int
        :returns: chunk data
        :rtype: bytes
        :raises SteamError: error message
        """
        if (depot_id, chunk_id) not in self._chunk_cache:
            resp = self.cdn_cmd('depot', '%s/chunk/%s' % (depot_id, chunk_id))

            data = symmetric_decrypt(resp.content, self.get_depot_key(app_id, depot_id))

            if data[:2] == b'VZ':
                if data[-2:] != b'zv':
                    raise SteamError("VZ: Invalid footer: %s" % repr(data[-2:]))
                if data[2:3] != b'a':
                    raise SteamError("VZ: Invalid version: %s" % repr(data[2:3]))

                vzfilter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, data[7:12])
                vzdec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[vzfilter])
                checksum, decompressed_size = struct.unpack('<II', data[-10:-2])
                # decompress_size is needed since lzma will sometime produce longer output
                # [12:-9] is need as sometimes lzma will produce shorter output
                # together they get us the right data
                data = vzdec.decompress(data[12:-9])[:decompressed_size]
                if crc32(data) != checksum:
                    raise SteamError("VZ: CRC32 checksum doesn't match for decompressed data")
            else:
                with ZipFile(BytesIO(data)) as zf:
                    data = zf.read(zf.filelist[0])

            self._chunk_cache[(depot_id, chunk_id)] = data

        return self._chunk_cache[(depot_id, chunk_id)]

    def get_manifest_request_code(self, app_id, depot_id, manifest_gid, branch='public', branch_password_hash=None):
        """Get manifest request code for authenticating manifest download

        :param app_id: App ID
        :type  app_id: int
        :param depot_id: Depot ID
        :type  depot_id: int
        :param manifest_gid: Manifest gid
        :type  manifest_gid: int
        :param branch: (optional) branch name
        :type  branch: str
        :param branch_password_hash: (optional) branch password hash
        :type  branch_password_hash: str
        :returns: manifest request code
        :rtype: int
        """

        body = {
            "app_id":      int(app_id),
            "depot_id":    int(depot_id),
            "manifest_id": int(manifest_gid),
        }

        if branch and branch.lower() != 'public':
            body['app_branch'] = branch

            if branch_password_hash:
                body['branch_password_hash'] = branch_password_hash

        resp = self.steam.send_um_and_wait(
            'ContentServerDirectory.GetManifestRequestCode#1',
            body,
            timeout=5,
        )

        if resp is None or resp.header.eresult != EResult.OK:
                raise SteamError("Failed to get manifest code for %s, %s, %s" % (app_id, depot_id, manifest_gid),
                                 EResult.Timeout if resp is None else EResult(resp.header.eresult))

        return resp.body.manifest_request_code

    def get_manifest(self, app_id, depot_id, manifest_gid, decrypt=True, manifest_request_code=0):
        """Download a manifest file

        :param app_id: App ID
        :type  app_id: int
        :param depot_id: Depot ID
        :type  depot_id: int
        :param manifest_gid: Manifest gid
        :type  manifest_gid: int
        :param decrypt: Decrypt manifest filenames
        :type  decrypt: bool
        :param manifest_request_code: Manifest request code, authenticates the download
        :type  manifest_request_code: int
        :returns: manifest instance
        :rtype: :class:`.CDNDepotManifest`
        """
        if (app_id, depot_id, manifest_gid) not in self.manifests:
            if manifest_request_code:
                resp = self.cdn_cmd('depot', '%s/manifest/%s/5/%s' % (depot_id, manifest_gid, manifest_request_code))
            else:
                resp = self.cdn_cmd('depot', '%s/manifest/%s/5' % (depot_id, manifest_gid))

            if resp.ok:
                manifest = self.DepotManifestClass(self, app_id, resp.content)
                if decrypt:
                    manifest.decrypt_filenames(self.get_depot_key(app_id, depot_id))
                self.manifests[(app_id, depot_id, manifest_gid)] = manifest

        return self.manifests[(app_id, depot_id, manifest_gid)]

    def check_beta_password(self, app_id, password):
        """Check branch beta password to unlock encrypted branches

        :param app_id: App ID
        :type  app_id: int
        :param password: beta password
        :type  password: str
        :returns: result
        :rtype: :class:`.EResult`
        """
        resp = self.steam.send_job_and_wait(MsgProto(EMsg.ClientCheckAppBetaPassword),
                                            {'app_id': app_id, 'betapassword': password})

        if resp.eresult == EResult.OK:
            self._LOG.debug("Unlocked following beta branches: %s",
                            ', '.join(map(lambda x: x.betaname.lower(), resp.betapasswords)))
            for entry in resp.betapasswords:
                self.beta_passwords[(app_id, entry.betaname.lower())] = unhexlify(entry.betapassword)
        else:
            self._LOG.debug("App beta password check failed. %r" % EResult(resp.eresult))

        return EResult(resp.eresult)

    def get_app_depot_info(self, app_id):
        if app_id not in self.app_depots:
            self.app_depots[app_id] = self.steam.get_product_info([app_id])['apps'][app_id]['depots']
        return self.app_depots[app_id]

    def has_license_for_depot(self, depot_id):
        """ Check if there is license for depot

        :param depot_id: depot ID
        :type  depot_id: int
        :returns: True if we have license
        :rtype: bool
        """
        if depot_id in self.licensed_depot_ids or depot_id in self.licensed_app_ids:
            return True
        else:
            return False

    def get_manifests(self, app_id, branch='public', password=None, filter_func=None, decrypt=True):
        """Get a list of CDNDepotManifest for app

        :param app_id: App ID
        :type  app_id: int
        :param branch: branch name
        :type  branch: str
        :param password: branch password for locked branches
        :type  password: str
        :param filter_func:
            Function to filter depots. ``func(depot_id, depot_info)``
        :returns: list of :class:`.CDNDepotManifest`
        :rtype: :class:`list` [:class:`.CDNDepotManifest`]
        :raises: ManifestError, SteamError
        """
        depots = self.get_app_depot_info(app_id)

        is_enc_branch = False

        if branch not in depots.get('branches', {}):
            raise SteamError("No branch named %s for app_id %s" % (repr(branch), app_id))
        elif int(depots['branches'][branch].get('pwdrequired', 0)) > 0:
            is_enc_branch = True

            if (app_id, branch) not in self.beta_passwords:
                if not password:
                    raise SteamError("Branch %r requires a password" % branch)

                result = self.check_beta_password(app_id, password)

                if result != EResult.OK:
                    raise SteamError("Branch password is not valid. %r" % result)

                if (app_id, branch) not in self.beta_passwords:
                    raise SteamError("Incorrect password for branch %r" % branch)

        def async_fetch_manifest(
            app_id, depot_id, manifest_gid, decrypt, depot_name, branch_name, branch_pass
        ):
            try:
                manifest_code = self.get_manifest_request_code(
                    app_id, depot_id, int(manifest_gid), branch_name, branch_pass
                )
            except SteamError as exc:
                return ManifestError("Failed to acquire manifest code", app_id, depot_id, manifest_gid, exc)

            try:
                manifest = self.get_manifest(
                    app_id, depot_id, manifest_gid, decrypt=decrypt, manifest_request_code=manifest_code
                )
            except Exception as exc:
                return ManifestError("Failed download", app_id, depot_id, manifest_gid, exc)

            manifest.name = depot_name
            return manifest

        tasks = []
        shared_depots = {}

        for depot_id, depot_info in iteritems(depots):
            if not depot_id.isdigit():
                continue

            depot_id = int(depot_id)

            # if filter_func set, use it to filter the list the depots
            if filter_func and not filter_func(depot_id, depot_info):
                continue

            # if we have no license for the depot, no point trying as we won't get depot_key
            if not self.has_license_for_depot(depot_id):
                self._LOG.debug("No license for depot %s (%s). Skipped",
                                repr(depot_info.get('name', depot_id)),
                                depot_id,
                                )
                continue

            # accumulate the shared depots
            if 'depotfromapp' in depot_info:
                shared_depots.setdefault(int(depot_info['depotfromapp']), set()).add(depot_id)
                continue


            # process depot, and get manifest for branch
            if is_enc_branch:
                egid = depot_info.get('encryptedmanifests', {}).get(branch, {}).get('encrypted_gid_2')

                if egid is not None:
                    manifest_gid = decrypt_manifest_gid_2(unhexlify(egid),
                                                          self.beta_passwords[(app_id, branch)])
                else:
                    manifest_gid = depot_info.get('manifests', {}).get('public')
            else:
                manifest_gid = depot_info.get('manifests', {}).get(branch)

            if manifest_gid is not None:
                tasks.append(
                    self.gpool.spawn(
                        async_fetch_manifest,
                        app_id,
                        depot_id,
                        manifest_gid,
                        decrypt,
                        depot_info.get('name', depot_id),
                        branch_name=branch,
                        branch_pass=None, # TODO: figure out how to pass this correctly
                  )
              )

        # collect results
        manifests = []

        for task in tasks:
            result = task.get()
            if isinstance(result, ManifestError):
                raise result
            manifests.append(result)

        # load shared depot manifests
        for app_id, depot_ids in iteritems(shared_depots):
            def nested_ffunc(depot_id, depot_info, depot_ids=depot_ids, ffunc=filter_func):
                return (int(depot_id) in depot_ids
                        and (ffunc is None or ffunc(depot_id,  depot_info)))

            manifests += self.get_manifests(app_id, filter_func=nested_ffunc)

        return manifests

    def iter_files(self, app_id, filename_filter=None, branch='public', password=None, filter_func=None):
        """Like :meth:`.get_manifests` but returns a iterator that goes through all the files
        in all the manifest.

        :param app_id: App ID
        :type  app_id: int
        :param filename_filter: wildcard filter for file paths
        :type  branch: str
        :param branch: branch name
        :type  branch: str
        :param password: branch password for locked branches
        :type  password: str
        :param filter_func:
            Function to filter depots. ``func(depot_id, depot_info)``
        :returns: generator of of CDN files
        :rtype: [:class:`.CDNDepotFile`]
        """
        for manifest in self.get_manifests(app_id, branch, password, filter_func):
            for fp in manifest.iter_files(filename_filter):
                yield fp

    def get_manifest_for_workshop_item(self, item_id):
        """Get the manifest file for a worshop item that is hosted on SteamPipe

        :param item_id: Workshop ID
        :type  item_id: int
        :returns: manifest instance
        :rtype: :class:`.CDNDepotManifest`
        :raises: ManifestError, SteamError
        """
        resp = self.steam.send_um_and_wait('PublishedFile.GetDetails#1', {
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

        if resp.header.eresult != EResult.OK:
            raise SteamError(resp.header.error_message or 'No message', resp.header.eresult)

        wf = None if resp is None else resp.body.publishedfiledetails[0]

        if wf is None or wf.result != EResult.OK:
            raise SteamError("Failed getting workshop file info",
                              EResult.Timeout if resp is None else EResult(wf.result))
        elif not wf.hcontent_file:
            raise SteamError("Workshop file is not on SteamPipe", EResult.FileNotFound)

        app_id = ws_app_id = wf.consumer_appid

        try:
            manifest_code = self.get_manifest_request_code(app_id, ws_app_id, int(wf.hcontent_file))
            manifest = self.get_manifest(app_id, ws_app_id, wf.hcontent_file, manifest_request_code=manifest_code)
        except SteamError as exc:
            return ManifestError("Failed to acquire manifest", app_id, depot_id, manifest_gid, exc)

        manifest.name = wf.title
        return manifest


