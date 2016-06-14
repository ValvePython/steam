"""Utility package with various useful functions
"""
import weakref
import struct
import socket
import sys

if sys.version_info < (3,):
    _range = xrange
else:
    _range = range

def ip_from_int(ip):
    """Convert IP to :py:class:`int`

    :param ip: IP in dot-decimal notation
    :type ip: str
    :rtype: int
    """
    return socket.inet_ntoa(struct.pack(">L", ip))

def ip_to_int(ip):
    """Convert :py:class:`int` to IP

    :param ip: int representing an IP
    :type ip: int
    :return: IP in dot-decimal notation
    :rtype: str
    """
    return struct.unpack(">L", socket.inet_aton(ip))[0]


protobuf_mask = 0x80000000

def is_proto(emsg):
    """
    :param emsg: emsg number
    :type emsg: int
    :return: True or False
    :rtype: bool
    """
    return (int(emsg) & protobuf_mask) > 0

def set_proto_bit(emsg):
    """
    :param emsg: emsg number
    :type emsg: int
    :return: emsg with proto bit set
    :rtype: int
    """
    return int(emsg) | protobuf_mask

def clear_proto_bit(emsg):
    """
    :param emsg: emsg number
    :type emsg: int
    :return: emsg with proto bit removed
    :rtype: int
    """
    return int(emsg) & ~protobuf_mask

def proto_to_dict(message):
    """Converts protobuf message instance to dict (shallow)

    :param message: protobuf message
    :return: parameters and their values
    :rtype: dict
    """
    return {field.name: getattr(message, field.name, field.default_value)
            for field in message.DESCRIPTOR.fields}

def chunks(arr, size):
    """Splits a list into chunks

    :param arr: list to split
    :type arr: :class:`list`
    :param size: number of elements in each chunk
    :type size: :class:`int`
    :return: generator object
    :rtype: :class:`generator`
    """
    for i in _range(0, len(arr), size):
        yield arr[i:i+size]


class WeakRefKeyDict(object):
    """Pretends to be a dictionary.
    Use any object (even unhashable) as key and store a value.
    Once the object is garbage collected, the entry is destroyed automatically.
    """
    def __init__(self):
        self.refs = {}

    def __setitem__(self, obj, value):
        key = id(obj)

        if key not in self.refs:
            wr = weakref.ref(obj, WeakRefCallback(self.refs, key))
            self.refs[key] = [wr, None]
        self.refs[key][1] = value

    def __getitem__(self, obj):
        key = id(obj)
        return self.refs[key][1]

    def __contains__(self, obj):
        return id(obj) in self.refs

    def __len__(self):
        return len(self.refs)

class WeakRefCallback(object):
    def __init__(self, refs, key):
        self.__dict__.update(locals())
    def __call__(self, wr):
        del self.refs[self.key]
