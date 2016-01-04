import struct
import socket


def ip_from_int(ip):
    return socket.inet_ntoa(struct.pack(">L", ip))

def ip_to_int(ip):
    return struct.unpack(">L", socket.inet_aton(ip))[0]
