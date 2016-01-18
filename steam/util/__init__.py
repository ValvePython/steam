"""Utility package with various useful functions
"""

import struct
import socket

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


