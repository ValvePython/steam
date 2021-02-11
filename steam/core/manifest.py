
from base64 import b64decode
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile
from struct import pack
from datetime import datetime
from fnmatch import fnmatch
import os.path

from steam.enums import EDepotFileFlag
from steam.core.crypto import symmetric_decrypt
from steam.utils.binary import StructReader
from steam.protobufs.content_manifest_pb2 import (ContentManifestMetadata,
                                                  ContentManifestPayload,
                                                  ContentManifestSignature)


class DepotFile(object):
    def __init__(self, manifest, file_mapping):
        """Depot file

        :param manifest: depot manifest
        :type  manifest: :class:`.DepotManifest`
        :param file_mapping: depot file mapping instance
        :type  file_mapping: ContentManifestPayload.FileMapping
        """
        if not isinstance(manifest, DepotManifest):
            raise TypeError("Expected 'manifest' to be of type DepotManifest")
        if not isinstance(file_mapping, ContentManifestPayload.FileMapping):
            raise TypeError("Expected 'file_mapping' to be of type ContentManifestPayload.FileMapping")

        self.manifest = manifest
        self.file_mapping = file_mapping

    def __repr__(self):
        return "<%s(%s, %s, %s, %s)>" % (
            self.__class__.__name__,
            self.manifest.depot_id,
            self.manifest.gid,
            repr(self.filename),
            'is_directory=True' if self.is_directory else self.size,
            )

    @property
    def filename_raw(self):
        """Filename with null terminator and whitespaces removed

        :type: str
        """
        return self.file_mapping.filename.rstrip('\x00 \n\t')

    @property
    def filename(self):
        """Filename matching the OS

        :type: str
        """
        return os.path.join(*self.filename_raw.split('\\'))
    
    @property
    def linktarget_raw(self):
        """Link target with null terminator and whitespaces removed

        :type: str
        """
        return self.file_mapping.linktarget.rstrip('\x00 \n\t')

    @property
    def linktarget(self):
        """Link target matching the OS

        :type: str
        """
        return os.path.join(*self.linktarget_raw.split('\\'))

    @property
    def size(self):
        """File size in bytes

        :type: int
        """
        return self.file_mapping.size

    @property
    def chunks(self):
        """File chunks instances

        :type: :class:`list` [ContentManifestPayload.FileMapping.ChunkData]
        """
        return self.file_mapping.chunks

    @property
    def flags(self):
        """File flags

        :type: :class:`.EDepotFileFlag`
        """
        return self.file_mapping.flags

    @property
    def is_directory(self):
        """:type: bool"""
        return self.flags & EDepotFileFlag.Directory > 0

    @property
    def is_symlink(self):
        """:type: bool"""
        return not not self.file_mapping.linktarget

    @property
    def is_file(self):
        """:type: bool"""
        return not self.is_directory and not self.is_symlink

    @property
    def is_executable(self):
        """:type: bool"""
        return self.flags & EDepotFileFlag.Executable > 0


class DepotManifest(object):
    DepotFileClass = DepotFile
    PROTOBUF_PAYLOAD_MAGIC = 0x71F617D0
    PROTOBUF_METADATA_MAGIC = 0x1F4812BE
    PROTOBUF_SIGNATURE_MAGIC = 0x1B81B817
    PROTOBUF_ENDOFMANIFEST_MAGIC = 0x32C415AB

    def __init__(self, data=None):
        """Represents depot manifest

        :param data: manifest data
        :type  data: bytes
        """
        self.metadata = ContentManifestMetadata()
        self.payload = ContentManifestPayload()
        self.signature = ContentManifestSignature()

        if data:
            self.deserialize(data)

    def __repr__(self):
        params = ', '.join([
                    "depot_id=" + str(self.depot_id),
                    "gid=" + str(self.gid),
                    "creation_time=" + repr(
                        datetime.utcfromtimestamp(self.metadata.creation_time).isoformat().replace('T', ' ')
                        ),
                    ])

        if self.metadata.filenames_encrypted:
            params += ', filenames_encrypted=True'

        return "<%s(%s)>" % (
            self.__class__.__name__,
            params,
            )

    @property
    def depot_id(self):
        """:type: int"""
        return self.metadata.depot_id

    @property
    def gid(self):
        """:type: int"""
        return self.metadata.gid_manifest

    @property
    def creation_time(self):
        """:type: int"""
        return self.metadata.creation_time

    @property
    def size_original(self):
        """:type: int"""
        return self.metadata.cb_disk_original

    @property
    def size_compressed(self):
        """:type: int"""
        return self.metadata.cb_disk_compressed

    @property
    def filenames_encrypted(self):
        """:type: bool"""
        return self.metadata.filenames_encrypted

    def decrypt_filenames(self, depot_key):
        """Decrypt all filenames in the manifest

        :param depot_key: depot key
        :type  depot_key: bytes
        :raises: :class:`RuntimeError`
        """
        if not self.metadata.filenames_encrypted:
            return

        try:
            for m in self.payload.mappings:
                m.filename = symmetric_decrypt(b64decode(m.filename), depot_key)

                if m.linktarget:
                    m.linktarget = symmetric_decrypt(b64decode(m.linktarget), depot_key)
        except Exception:
            raise RuntimeError("Unable to decrypt filename for depot manifest")

        self.metadata.filenames_encrypted = False

    def deserialize(self, data):
        """Deserialize a manifest (compressed or uncompressed)

        :param data: manifest data
        :type  data: bytes
        """
        try:
            with ZipFile(BytesIO(data)) as zf:
                data = zf.read(zf.filelist[0])
        except BadZipFile:
            pass

        data = StructReader(data)

        magic, length = data.unpack('<II')

        if magic != DepotManifest.PROTOBUF_PAYLOAD_MAGIC:
            raise Exception("Expecting protobuf payload")

        self.payload = ContentManifestPayload()
        self.payload.ParseFromString(data.read(length))

        magic, length = data.unpack('<II')

        if magic != DepotManifest.PROTOBUF_METADATA_MAGIC:
            raise Exception("Expecting protobuf metadata")

        self.metadata = ContentManifestMetadata()
        self.metadata.ParseFromString(data.read(length))

        magic, length = data.unpack('<II')

        if magic != DepotManifest.PROTOBUF_SIGNATURE_MAGIC:
            raise Exception("Expecting protobuf signature")

        self.signature = ContentManifestSignature()
        self.signature.ParseFromString(data.read(length))

        magic, = data.unpack('<I')

        if magic != DepotManifest.PROTOBUF_ENDOFMANIFEST_MAGIC:
            raise Exception("Expecting end of manifest")

    def serialize(self, compress=True):
        """Serialize manifest

        :param compress: wether the output should be Zip compressed
        :type  compress: bytes
        """
        data = BytesIO()

        part = self.payload.SerializeToString()
        data.write(pack('<II', DepotManifest.PROTOBUF_PAYLOAD_MAGIC, len(part)))
        data.write(part)

        part = self.metadata.SerializeToString()
        data.write(pack('<II', DepotManifest.PROTOBUF_METADATA_MAGIC, len(part)))
        data.write(part)

        part = self.signature.SerializeToString()
        data.write(pack('<II', DepotManifest.PROTOBUF_SIGNATURE_MAGIC, len(part)))
        data.write(part)

        data.write(pack('<I', DepotManifest.PROTOBUF_ENDOFMANIFEST_MAGIC))

        if compress:
            zbuff = BytesIO()
            with ZipFile(zbuff, 'w', ZIP_DEFLATED) as zf:
                zf.writestr('z', data.getvalue())

            return zbuff.getvalue()
        else:
            return data.getvalue()

    def __iter__(self):
        if not self.filenames_encrypted:
            for mapping in self.payload.mappings:
                yield self.DepotFileClass(self, mapping)

    def iter_files(self, pattern=None):
        """
        :param pattern: unix shell wildcard pattern, see :func:`.fnmatch`
        :type  pattern: str
        """
        if not self.filenames_encrypted:
            for mapping in self.payload.mappings:
                if (pattern is not None
                   and not fnmatch(mapping.filename.rstrip('\x00 \n\t'), pattern)):
                    continue
                yield self.DepotFileClass(self, mapping)

    def __len__(self):
        return len(self.payload.mappings)


