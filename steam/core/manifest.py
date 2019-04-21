
from base64 import b64decode
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED
from struct import pack
from datetime import datetime

from steam.core.crypto import symmetric_decrypt
from steam.util.binary import StructReader
from steam.protobufs.content_manifest_pb2 import (ContentManifestMetadata,
                                                  ContentManifestPayload,
                                                  ContentManifestSignature)


class DepotManifest(object):
    PROTOBUF_PAYLOAD_MAGIC = 0x71F617D0
    PROTOBUF_METADATA_MAGIC = 0x1F4812BE
    PROTOBUF_SIGNATURE_MAGIC = 0x1B81B817
    PROTOBUF_ENDOFMANIFEST_MAGIC = 0x32C415AB

    def __init__(self, data):
        self.metadata = ContentManifestMetadata()
        self.payload = ContentManifestPayload()
        self.signature = ContentManifestSignature()

        if data:
            self.deserialize(data)

    def __repr__(self):
        params = ', '.join([
                    str(self.metadata.depot_id),
                    str(self.metadata.gid_manifest),
                    repr(datetime.utcfromtimestamp(self.metadata.creation_time).isoformat().replace('T', ' ')),
                    ])

        if self.metadata.filenames_encrypted:
            params += ', filenames_encrypted=True'

        return "<%s(%s)>" % (
            self.__class__.__name__,
            params,
            )

    def decrypt_filenames(self, depot_key):
        if not self.metadata.filenames_encrypted:
            return True

        for mapping in self.payload.mappings:
            filename = b64decode(mapping.filename)

            try:
                filename = symmetric_decrypt(filename, depot_key)
            except Exception:
                print("Unable to decrypt filename for depot manifest")
                return False

            mapping.filename = filename

        self.metadata.filenames_encrypted = False
        return True

    def deserialize(self, data):
        with ZipFile(BytesIO(data)) as zf:
            data = StructReader(zf.read(zf.filelist[0]))

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

    def serialize(self):
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

        zbuff = BytesIO()
        with ZipFile(zbuff, 'w', ZIP_DEFLATED) as zf:
            zf.writestr('z', data.getvalue())

        return zbuff.getvalue()
