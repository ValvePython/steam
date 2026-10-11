import bz2
from binascii import crc32
from struct import pack
import unittest

import mock

from steam.game_servers import _handle_a2s_response, a2s_rules


def compressed_packet(data, checksum=None, size=None):
    if checksum is None:
        checksum = crc32(data) & 0xffffffff
    if size is None:
        size = len(data)
    return (pack('<lLBB', -2, 0x80000001, 1, 0)
            + pack('<LL', size, checksum) + bz2.compress(data))


class TestCompressedA2SResponse(unittest.TestCase):
    @mock.patch('socket.socket')
    def test_rules_with_checksum_high_bit(self, socket_class):
        data = b'\xff\xff\xff\xffE\x01\x00key\x00one\x00'
        self.assertGreater(crc32(data) & 0xffffffff, 0x7fffffff)
        socket_class.return_value.recv.side_effect = [
            b'\xff\xff\xff\xffA\x01\x02\x03\x04',
            compressed_packet(data),
        ]

        self.assertEqual({'key': 'one'}, a2s_rules(('addr', 1234)))
        socket_class.return_value.close.assert_called_once_with()

    def test_checksum_without_high_bit(self):
        data = b'\xff\xff\xff\xffE\x01\x00key\x00value\x00'
        self.assertLess(crc32(data) & 0xffffffff, 0x80000000)
        sock = mock.Mock()
        sock.recv.return_value = compressed_packet(data)

        self.assertEqual(data, _handle_a2s_response(sock))

    def test_signed_crc32_result(self):
        data = b'\xff\xff\xff\xffE\x01\x00key\x00one\x00'
        sock = mock.Mock()
        sock.recv.return_value = compressed_packet(data)
        # Python 2 returns a signed crc32; compare the same 32-bit pattern.
        with mock.patch('steam.game_servers.crc32',
                        return_value=crc32(data) - 0x100000000):
            self.assertEqual(data, _handle_a2s_response(sock))

    def test_corrupted_checksum_still_rejected(self):
        data = b'\xff\xff\xff\xffE\x01\x00key\x00one\x00'
        sock = mock.Mock()
        sock.recv.return_value = compressed_packet(
            data, checksum=(crc32(data) & 0xffffffff) ^ 1)

        with self.assertRaises(RuntimeError) as raised:
            _handle_a2s_response(sock)
        self.assertIn('Response checksum mismatch', str(raised.exception))

    def test_wrong_decompressed_size_still_rejected(self):
        data = b'\xff\xff\xff\xffE\x01\x00key\x00one\x00'
        sock = mock.Mock()
        sock.recv.return_value = compressed_packet(data, size=len(data) + 1)

        with self.assertRaises(RuntimeError) as raised:
            _handle_a2s_response(sock)
        self.assertIn('Response size mismatch', str(raised.exception))
