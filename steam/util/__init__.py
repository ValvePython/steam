import struct
import socket


def ip_from_int(ip):
    return socket.inet_ntoa(struct.pack(">L", ip))

def ip_to_int(ip):
    return struct.unpack(">L", socket.inet_aton(ip))[0]


protobuf_mask = 0x80000000

def is_proto(emsg):
    return (int(emsg) & protobuf_mask) > 0

def set_proto_bit(emsg):
    return int(emsg) | protobuf_mask

def clear_proto_bit(emsg):
    return int(emsg) & ~protobuf_mask


