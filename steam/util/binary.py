import struct

class StructReader(object):
    def __init__(self, data):
        """Simplifies parsing of struct data from bytes

        :param data: data bytes
        :type  data: :class:`bytes`
        """
        if not isinstance(data, bytes):
            raise ValueError("Requires bytes")
        self.data = data
        self.offset = 0

    def read_cstring(self):
        """Reads a single null termianted string

        :return: string without bytes
        :rtype: :class:`bytes`
        """
        null_index = self.data.find(b'\x00', self.offset)
        text = self.data[self.offset:null_index]  # bytes without the null
        self.offset = null_index + 1  # advanced past null
        return text

    def read_format(self, format_text):
        """Unpack bytes using struct modules format

        :param format_text: struct's module format
        :type  format_text: :class:`str`
        :return data: result from :func:`struct.unpack_from`
        :rtype: :class:`tuple`
        """
        data = struct.unpack_from(format_text, self.data, self.offset)
        self.offset += struct.calcsize(format_text)
        return data

    def skip(self, n):
        """Skips the next ``n`` bytes

        :param n: number of bytes to skip
        :type  n: :class:`int`
        """
        self.offset += n
