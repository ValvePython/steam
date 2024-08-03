"""
Appache file parsing examples:

.. code:: python

    >>> from steam.utils.appcache import parse_appinfo, parse_packageinfo

    >>> header, apps = parse_appinfo(open('/d/Steam/appcache/appinfo.vdf', 'rb'))
    >>> header
    {'magic': b")DV\\x07", 'universe': 1}
    >>> next(apps)
    {'appid': 5,
     'size': 79,
     'info_state': 1,
     'last_updated': 1484735377,
     'access_token': 0,
     'sha1': b'\\x87\\xfaCg\\x85\\x80\\r\\xb4\\x90Im\\xdc}\\xb4\\x81\\xeeQ\\x8b\\x825',
     'change_number': 4603827,
     'data_sha1': b'\\x87\\xfaCg\\x85\\x80\\r\\xb4\\x90Im\\xdc}\\xb4\\x81\\xeeQ\\x8b\\x825',
     'data': {'appinfo': {'appid': 5, 'public_only': 1}}}

    >>> header, pkgs = parse_packageinfo(open('/d/Steam/appcache/packageinfo.vdf', 'rb'))
    >>> header
    {'magic': b"'UV\\x06", 'universe': 1}

    >>> next(pkgs)
    {'packageid': 7,
     'sha1': b's\\x8b\\xf7n\\t\\xe5 k#\\xb6-\\x82\\xd2 \\x14k@\\xfeDQ',
     'change_number': 7469765,
     'data': {'7': {'packageid': 7,
       'billingtype': 1,
       'licensetype': 1,
       'status': 0,
       'extended': {'requirespreapproval': 'WithRedFlag'},
       'appids': {'0': 10, '1': 80, '2': 100, '3': 254430},
       'depotids': {'0': 0, '1': 95, '2': 101, '3': 102, '4': 103, '5': 254431},
       'appitems': {}}}}

"""

import struct
from vdf import binary_load

uint32 = struct.Struct('<I')
uint64 = struct.Struct('<Q')
int64 = struct.Struct('<q')

def parse_appinfo(fp):
    """Parse appinfo.vdf from the Steam appcache folder

    :param fp: file-like object
    :raises: SyntaxError
    :rtype: (:class:`dict`, :class:`Generator`)
    :return: (header, apps iterator)
    """
# format:
#   uint32   - MAGIC: "'DV\x07" or "(DV\x07" or b")DV\x07"
#   uint32   - UNIVERSE: 1
#   int64    - OFFSET TO KEY TABLE (added in ")DV\x07")
#   ---- repeated app sections ----
#   uint32   - AppID
#   uint32   - size
#   uint32   - infoState
#   uint32   - lastUpdated
#   uint64   - accessToken
#   20bytes  - SHA1
#   uint32   - changeNumber
#   20bytes  - binary_vdf SHA1 (added in "(DV\x07")
#   variable - binary_vdf
#   ---- end of section ---------
#   uint32   - EOF: 0
#
#   ---- key table ----
#   uint32   - Count of keys
#   char[]   - Null-terminated strings corresponding to field names

    magic = fp.read(4)
    if magic not in (b"'DV\x07", b"(DV\x07", b")DV\x07"):
        raise SyntaxError("Invalid magic, got %s" % repr(magic))

    universe = uint32.unpack(fp.read(4))[0]

    key_table = None

    appinfo_version = magic[0]
    if appinfo_version >= 41:  # b')'
        # appinfo.vdf V29 and newer store list of keys in separate table at the
        # end of the file to reduce size. Retrieve it and pass it to the VDF
        # parser later.
        key_table = []

        key_table_offset = struct.unpack('q', fp.read(8))[0]
        offset = fp.tell()
        fp.seek(key_table_offset)
        key_count = uint32.unpack(fp.read(4))[0]

        # Read all null-terminated strings into a list
        for _ in range(0, key_count):
            field_name = bytearray()
            while True:
                field_name += fp.read(1)

                if field_name[-1] == 0:
                    field_name = field_name[0:-1]
                    field_name = field_name.decode('utf-8', 'replace')

                    key_table.append(field_name)
                    break

        # Rewind to the beginning of the file after the header:
        # we can now parse the rest of the file.
        fp.seek(offset)

    def apps_iter():
        while True:
            appid = uint32.unpack(fp.read(4))[0]

            if appid == 0:
                break

            app = {
                'appid': appid,
                'size': uint32.unpack(fp.read(4))[0],
                'info_state': uint32.unpack(fp.read(4))[0],
                'last_updated': uint32.unpack(fp.read(4))[0],
                'access_token': uint64.unpack(fp.read(8))[0],
                'sha1': fp.read(20),
                'change_number': uint32.unpack(fp.read(4))[0],
            }

            if magic != b"'DV\x07":
                app['data_sha1'] = fp.read(20)

            # 'key_table' will be None for older 'appinfo.vdf' files which
            # use self-contained binary VDFs.
            app['data'] = binary_load(fp, key_table=key_table)

            yield app


    return ({
              'magic': magic,
              'universe': universe,
            },
            apps_iter()
            )

def parse_packageinfo(fp):
    """Parse packageinfo.vdf from the Steam appcache folder

    :param fp: file-like object
    :raises: SyntaxError
    :rtype: (:class:`dict`, :class:`Generator`)
    :return: (header, packages iterator)
    """
# format:
#   uint32   - MAGIC: b"'UV\x06" or b"(UV\x06"
#   uint32   - UNIVERSE: 1
#   ---- repeated package sections ----
#   uint32   - PackageID
#   20bytes  - SHA1
#   uint32   - changeNumber
#   uint64   - token           (only on b"(UV\x06")
#   variable - binary_vdf
#   ---- end of section ---------
#   uint32   - EOF: 0xFFFFFFFF

    magic = fp.read(4)
    if magic not in (b"'UV\x06", b"(UV\x06"):
        raise SyntaxError("Invalid magic, got %s" % repr(magic))

    universe = uint32.unpack(fp.read(4))[0]

    def pkgs_iter():
        while True:
            packageid = uint32.unpack(fp.read(4))[0]

            if packageid == 0xFFFFFFFF:
                break

            pkg = {
                'packageid': packageid,
                'sha1': fp.read(20),
                'change_number': uint32.unpack(fp.read(4))[0],
            }

            if magic == b"(UV\x06":
                pkg['token'] = uint64.unpack(fp.read(8))[0]

            pkg['data'] = binary_load(fp)

            yield pkg


    return ({
              'magic': magic,
              'universe': universe,
            },
            pkgs_iter()
            )
