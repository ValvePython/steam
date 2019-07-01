"""
The :class:`.CDNClient` class provides a simple API for downloading Steam content from SteamPipe

Initializing :class:`.CDNClient` requires a logged in :class:`.SteamClient` instance

.. code:: python

    mysteam = SteamClient()
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
from steam.core.msg import MsgProto
from steam.enums import EResult, EServerType, EType
from steam.enums.emsg import EMsg
from steam.util.web import make_requests_session
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
    servers = deque()  #: CS Server list
    _chunk_cache = LRUCache(20)
    cell_id = 0  #: Cell ID to use, initialized from SteamClient instance

    def __init__(self, client):
        """CDNClient allows loading and reading of manifests for Steam apps are used
        to list and download content

        :param client: logged in SteamClient instance
        :type  client: :class:`.SteamClient`
        """
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

    def load_licenses(self):
        """Read licenses from SteamClient instance, required for determining accessible content"""
        self.licensed_app_ids.clear()
        self.licensed_depot_ids.clear()

        if self.steam.steam_id.type == EType.AnonUser:
            packages = [17906]
        else:
            if not self.steam.licenses:
                self._LOG.debug("No steam licenses available. Is SteamClient instances connected?")
                return

            packages = list(self.steam.licenses.keys())

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
        self.servers.extend(servers)

        if not self.servers:
            raise ValueError("Failed to fetch content servers")

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
        """
        if (app_id, depot_id) not in self.depot_keys:
            msg = self.steam.get_depot_key(app_id, depot_id)

            if msg and msg.eresult == EResult.OK:
                self.depot_keys[(app_id, depot_id)] = msg.depot_encryption_key
            else:
                raise ValueError("Failed getting depot key: %s" % repr(
                    EResult.Timeout if msg is None else EResult(msg.eresult)))

        return self.depot_keys[(app_id, depot_id)]

    def get(self, command, args):
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
                resp = self.web.get(url)
            except:
                pass
            else:
                if resp.ok:
                    return resp
                elif resp.status_code in (401, 403, 404):
                    resp.raise_for_status()

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
        """
        if (depot_id, chunk_id) not in self._chunk_cache:
            resp = self.get('depot', '%s/chunk/%s' % (depot_id, chunk_id))

            data = symmetric_decrypt(resp.content, self.get_depot_key(app_id, depot_id))

            if data[:2] == b'VZ':
                if data[-2:] != b'zv':
                    raise ValueError("VZ: Invalid footer: %s" % repr(data[-2:]))
                if data[2:3] != b'a':
                    raise ValueError("VZ: Invalid version: %s" % repr(data[2:3]))

                vzfilter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, data[7:12])
                vzdec = lzma.LZMADecompressor(lzma.FORMAT_RAW, filters=[vzfilter])
                checksum, decompressed_size = struct.unpack('<II', data[-10:-2])
                # i have no idea why, but some chunks will decompress with 1 extra byte at the end
                data = vzdec.decompress(data[12:-10])[:decompressed_size]
                if crc32(data) != checksum:
                    raise ValueError("VZ: CRC32 checksum doesn't match for decompressed data")
            else:
                with ZipFile(BytesIO(data)) as zf:
                    data = zf.read(zf.filelist[0])

            self._chunk_cache[(depot_id, chunk_id)] = data

        return self._chunk_cache[(depot_id, chunk_id)]

    def get_manifest(self, app_id, depot_id, manifest_gid, decrypt=True):
        """Download a manifest file

        :param app_id: App ID
        :type  app_id: int
        :param depot_id: Depot ID
        :type  depot_id: int
        :param manifest_gid: Manifest gid
        :type  manifest_gid: int
        :param decrypt: Decrypt manifest filenames
        :type  decrypt: bool
        :returns: manifest instance
        :rtype: :class:`.CDNDepotManifest`
        """
        if (app_id, depot_id, manifest_gid) not in self.manifests:
            resp = self.get('depot', '%s/manifest/%s/5' % (depot_id, manifest_gid))

            if resp.ok:
                manifest = CDNDepotManifest(self, app_id, resp.content)
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

    def get_manifests(self, app_id, branch='public', password=None, filter_func=None):
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
        """
        if app_id not in self.app_depots:
            self.app_depots[app_id] = self.steam.get_product_info([app_id])['apps'][app_id]['depots']
        depots = self.app_depots[app_id]

        is_enc_branch = False

        if branch not in depots['branches']:
            raise ValueError("No branch named %s for app_id %s" % (repr(branch), app_id))
        elif int(depots['branches'][branch].get('pwdrequired', 0)) > 0:
            is_enc_branch = True

            if (app_id, branch) not in self.beta_passwords:
                if not password:
                    raise ValueError("Branch %r requires a password" % branch)

                result = self.check_beta_password(app_id, password)

                if result != EResult.OK:
                    raise ValueError("Branch password is not valid. %r" % result)

                if (app_id, branch) not in self.beta_passwords:
                    raise ValueError("Incorrect password for branch %r" % branch)

        def async_fetch_manifest(app_id, depot_id, manifest_gid, name):
            manifest = self.get_manifest(app_id, depot_id, manifest_gid)
            manifest.name = name
            return manifest

        tasks = []
        gpool = GPool(8)

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
                tasks.append(gpool.spawn(self.get_manifests,
                                         int(depot_info['depotfromapp']),
                                         filter_func=(lambda a, b: int(a) == depot_id),
                                         ))
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
                tasks.append(gpool.spawn(async_fetch_manifest,
                                         app_id,
                                         depot_id,
                                         manifest_gid,
                                         depot_info['name'],
                                         ))

        manifests = []

        for task in tasks:
            try:
                result = task.get()
            except ValueError as exp:
                self._LOG.error("Depot %s (%s): %s",
                                repr(depot_info['name']),
                                depot_id,
                                str(exp),
                                )
            else:
                if isinstance(result, list):
                    manifests.extend(result)
                else:
                    manifests.append(result)

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
        :rtype: :class:`.CDNDepotFile`
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
        :raises: steam error
        :rtype: :class:`.SteamError`
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
            raise SteamError(resp.header.error_message, resp.header.eresult)

        wf = None if resp is None else resp.body.publishedfiledetails[0]

        if wf is None or wf.result != EResult.OK:
            raise ValueError("Failed getting workshop file info: %s" % repr(
                EResult.Timeout if resp is None else EResult(wf.result)))
        elif not wf.hcontent_file:
            raise ValueError("Workshop file is not on SteamPipe")

        app_id = ws_app_id = wf.consumer_appid

        manifest = self.get_manifest(app_id, ws_app_id, wf.hcontent_file)
        manifest.name = wf.title
        return manifest


class CDNDepotManifest(DepotManifest):
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

        :param length: number of bytes to read. Read the whole if not set
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
