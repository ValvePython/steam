from struct import unpack_from as _unpack_from, calcsize as _calcsize


class StructReader(object):
    def __init__(self, data):
        """Simplifies parsing of struct data from bytes

        :param data: data bytes
        :type  data: :class:`bytes`
        """
        if not isinstance(data, bytes):
            raise ValueError("Only works with bytes")
        self.data = data
        self.offset = 0

    def __len__(self):
        return len(self.data)

    def rlen(self):
        """Number of remaining bytes that can be read

        :return: number of remaining bytes
        :rtype: :class:`int`
        """
        return max(0, len(self) - self.offset)

    def read(self, n=1):
        """Return n bytes

        :param n: number of bytes to return
        :type  n: :class:`int`
        :return: bytes
        :rtype: :class:`bytes`
        """
        self.offset += n
        return self.data[self.offset - n:self.offset]

    def read_cstring(self, terminator=b'\x00'):
        """Reads a single null termianted string

        :return: string without bytes
        :rtype: :class:`bytes`
        """
        null_index = self.data.find(terminator, self.offset)
        if null_index == -1:
            raise RuntimeError("Reached end of buffer")
        result = self.data[self.offset:null_index]  # bytes without the terminator
        self.offset = null_index + len(terminator)  # advance offset past terminator
        return result

    def unpack(self, format_text):
        """Unpack bytes using struct modules format

        :param format_text: struct's module format
        :type  format_text: :class:`str`
        :return data: result from :func:`struct.unpack_from`
        :rtype: :class:`tuple`
        """
        data = _unpack_from(format_text, self.data, self.offset)
        self.offset += _calcsize(format_text)
        return data

    def skip(self, n):
        """Skips the next ``n`` bytes

        :param n: number of bytes to skip
        :type  n: :class:`int`
        """
        self.offset += n
