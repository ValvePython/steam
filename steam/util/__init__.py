"""Utility package with various useful functions
"""
import weakref
import struct
import socket
import sys
import six
from six.moves import xrange as _range
from types import GeneratorType as _GeneratorType
from google.protobuf.message import Message as _ProtoMessageType

if six.PY2:
    _list_types = list, xrange, _GeneratorType
else:
    _list_types = list, range, _GeneratorType, map, filter


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
    """Converts protobuf message instance to dict

    :param message: protobuf message instance
    :return: parameters and their values
    :rtype: dict
    :raises: :class:`.TypeError` if ``message`` is not a proto message
    """
    if not isinstance(message, _ProtoMessageType):
        raise TypeError("Expected `message` to be a instance of protobuf message")

    data = {}

    for desc, field in message.ListFields():
        if desc.type == desc.TYPE_MESSAGE:
            if desc.label == desc.LABEL_REPEATED:
                data[desc.name] = list(map(proto_to_dict, field))
            else:
                data[desc.name] = proto_to_dict(field)
        else:
            data[desc.name] = list(field) if desc.label == desc.LABEL_REPEATED else field

    return data

def proto_fill_from_dict(message, data, clear=True):
    """Fills protobuf message parameters inplace from a :class:`dict`

    :param message: protobuf message instance
    :param data: parameters and values
    :type data: dict
    :param clear: whether clear exisiting values
    :type clear: bool
    :return: value of message paramater
    :raises: incorrect types or values will raise
    """
    if not isinstance(message, _ProtoMessageType):
        raise TypeError("Expected `message` to be a instance of protobuf message")
    if not isinstance(data, dict):
        raise TypeError("Expected `data` to be of type `dict`")

    if clear: message.Clear()
    field_descs = message.DESCRIPTOR.fields_by_name

    for key, val in data.items():
        desc = field_descs[key]

        if desc.type == desc.TYPE_MESSAGE:
            if desc.label == desc.LABEL_REPEATED:
                if not isinstance(val, _list_types):
                    raise TypeError("Expected %s to be of type list, got %s" % (repr(key), type(val)))

                list_ref = getattr(message, key)

                # Takes care of overwriting list fields when merging partial data (clear=False)
                if not clear: del list_ref[:]  # clears the list

                for item in val:
                    item_message = getattr(message, key).add()
                    proto_fill_from_dict(item_message, item)
            else:
                if not isinstance(val, dict):
                    raise TypeError("Expected %s to be of type dict, got %s" % (repr(key), type(dict)))

                proto_fill_from_dict(getattr(message, key), val)
        else:
            if isinstance(val, _list_types):
                list_ref = getattr(message, key)
                if not clear: del list_ref[:]  # clears the list
                list_ref.extend(val)
            else:
                setattr(message, key, val)

    return message

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
