import unittest
import steam.util as ut
import steam.util.web as uweb
import requests

proto_mask = 0x80000000

class Util_Functions(unittest.TestCase):
    def test_ip_from_int(self):
        self.assertEqual('0.0.0.0', ut.ip_from_int(0))
        self.assertEqual('12.34.56.78', ut.ip_from_int(203569230))
        self.assertEqual('255.255.255.255', ut.ip_from_int(4294967295))

    def test_ip_to_int(self):
        self.assertEqual(ut.ip_to_int('0.0.0.0'), 0)
        self.assertEqual(ut.ip_to_int('12.34.56.78'), 203569230)
        self.assertEqual(ut.ip_to_int('255.255.255.255'), 4294967295)

    def test_is_proto(self):
        self.assertTrue(ut.is_proto(proto_mask))
        self.assertTrue(ut.is_proto(proto_mask | 123456))
        self.assertFalse(ut.is_proto(0))
        self.assertFalse(ut.is_proto(proto_mask - 1))
        self.assertFalse(ut.is_proto(proto_mask << 1))

    def test_set_proto_big(self):
        self.assertFalse(ut.is_proto(0))
        self.assertTrue(ut.is_proto(ut.set_proto_bit(0)))
        self.assertFalse(ut.is_proto(1))
        self.assertTrue(ut.is_proto(ut.set_proto_bit(1)))

    def test_clear_proto_big(self):
        self.assertEqual(ut.clear_proto_bit(0), 0)
        self.assertEqual(ut.clear_proto_bit(123), 123)
        self.assertEqual(ut.clear_proto_bit(proto_mask | 123), 123)
        self.assertEqual(ut.clear_proto_bit((proto_mask - 1) | proto_mask), proto_mask - 1)

    def test_make_requests_session(self):
        self.assertIsInstance(uweb.make_requests_session(), requests.Session)
