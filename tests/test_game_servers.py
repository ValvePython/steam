import mock
import socket
import unittest

from steam.game_servers import a2s_rules


class TestA2SRules(unittest.TestCase):
    @mock.patch("socket.socket")
    def test_returns_rules_with_default_arguments(self, mock_socket_class):
        mock_socket = mock_socket_class.return_value
        mock_socket.recv.side_effect = [
            b"\xff\xff\xff\xffA\x01\x02\x03\x04",
            b"\xff\xff\xff\xffE\x03\0text\0b\x99r\0int\x0042\0float\x0021.12\0"
        ]

        rules = a2s_rules(("addr", 1234))

        self.assertEqual(
            {
                "text": u"b\ufffdr",
                "int": 42,
                "float": 21.12
            },
            rules)

        mock_socket_class.assert_called_once_with(
            socket.AF_INET, socket.SOCK_DGRAM)

        mock_socket.connect.assert_called_once_with(("addr", 1234))
        mock_socket.settimeout.assert_called_once_with(2)

        self.assertEqual(2, mock_socket.send.call_count)
        mock_socket.send.assert_has_calls([
            mock.call(b"\xff\xff\xff\xffV\0\0\0\0"),
            mock.call(b"\xff\xff\xff\xffV\x01\x02\x03\x04")
        ])

        self.assertEqual(2, mock_socket.recv.call_count)
        mock_socket.recv.assert_has_calls([
            mock.call(512),
            mock.call(2048)
        ])

        mock_socket.close.assert_called_once_with()

    @mock.patch("socket.socket")
    def test_returns_rules_as_bytes_when_binary_is_true(
            self, mock_socket_class):
        mock_socket = mock_socket_class.return_value
        mock_socket.recv.side_effect = [
            b"\xff\xff\xff\xffA\x01\x02\x03\x04",
            b"\xff\xff\xff\xffE\x03\0text\0b\x99r\0int\x0042\0float\x0021.12\0"
        ]

        rules = a2s_rules(("addr", 1234), binary=True)

        self.assertEqual(
            {
                b"text": b"b\x99r",
                b"int": b"42",
                b"float": b"21.12"
            },
            rules)
