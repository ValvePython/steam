import unittest
import steam.util as ut
import steam.util.web as uweb
import requests
from steam.protobufs.test_messages_pb2 import ComplexProtoMessage

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

class Util_Proto(unittest.TestCase):
    def setUp(self):
        self.msg = ComplexProtoMessage()

    def cleanUp(self):
        self.msg.Clear()

    def test_proto_from_dict_to_dict(self):
        DATA = {'buffers': [
                  {'data': b'some data',        'flags': [{'flag': True}, {'flag': False}, {'flag': False}]},
                  {'data': b'\x01\x02\x03\x04', 'flags': [{'flag': False}, {'flag': True}, {'flag': True}]}
                  ],
                'list_number32': [4,16,64,256,1024,4096,16384,65536,262144,1048576,4194304,16777216,67108864,268435456,1073741824],
                'list_number64': [4,64,1024,16384,262144,1125899906842624,18014398509481984,288230376151711744,4611686018427387904],
                'messages': [{'text': 'test string'}, {'text': 'another one'}, {'text': 'third'}],
                'number32': 16777216,
                'number64': 72057594037927936
                }

        ut.proto_fill_from_dict(self.msg, DATA)

        RESULT = ut.proto_to_dict(self.msg)

        self.assertEqual(DATA, RESULT)

    def test_proto_from_dict_merge(self):
        self.msg.list_number32.extend([1,2,3])

        ut.proto_fill_from_dict(self.msg, {'list_number32': [4,5,6]}, clear=False)

        self.assertEqual(self.msg.list_number32, [4,5,6])

    def test_proto_from_dict_merge_dict(self):
        self.msg.messages.add(text='one')
        self.msg.messages.add(text='two')

        ut.proto_fill_from_dict(self.msg, {'messages': [{'text': 'three'}]}, clear=False)

        self.assertEqual(len(self.msg.messages), 1)
        self.assertEqual(self.msg.messages[0].text, 'three')

    def test_proto_from_dict__dict_insteadof_list(self):
        with self.assertRaises(TypeError):
            ut.proto_fill_from_dict(self.msg, {'list_number32': [{}, {}]})

    def test_proto_from_dict__list_insteadof_dict(self):
        with self.assertRaises(TypeError):
            ut.proto_fill_from_dict(self.msg, {'messages': [1,2,3]})

    def test_proto_fill_from_dict__list(self):
        ut.proto_fill_from_dict(self.msg, {'list_number32': [1,2,3]})
        self.assertEqual(self.msg.list_number32, [1,2,3])

    def test_proto_fill_from_dict__dict_list(self):
        ut.proto_fill_from_dict(self.msg, {'messages': [{'text': 'one'}, {'text': 'two'}]})
        self.assertEqual(len(self.msg.messages), 2)
        self.assertEqual(self.msg.messages[0].text, 'one')
        self.assertEqual(self.msg.messages[1].text, 'two')

    def test_proto_fill_from_dict__list(self):
        ut.proto_fill_from_dict(self.msg, {'list_number32': range(10)})
        self.assertEqual(self.msg.list_number32, list(range(10)))


    def test_proto_fill_from_dict__generator(self):
        ut.proto_fill_from_dict(self.msg, {'list_number32': (x for x in [1,2,3])})
        self.assertEqual(self.msg.list_number32, [1,2,3])

    def test_proto_fill_from_dict__dict_generator(self):
        ut.proto_fill_from_dict(self.msg, {'messages': (x for x in [{'text': 'one'}, {'text': 'two'}])})
        self.assertEqual(len(self.msg.messages), 2)
        self.assertEqual(self.msg.messages[0].text, 'one')
        self.assertEqual(self.msg.messages[1].text, 'two')

    def test_proto_fill_from_dict__func_generator(self):
        def number_gen():
            yield 1
            yield 2
            yield 3

        ut.proto_fill_from_dict(self.msg, {'list_number32': number_gen()})
        self.assertEqual(self.msg.list_number32, [1,2,3])

    def test_proto_fill_from_dict__dict_func_generator(self):
        def dict_gen():
            yield {'text': 'one'}
            yield {'text': 'two'}

        ut.proto_fill_from_dict(self.msg, {'messages': dict_gen()})
        self.assertEqual(len(self.msg.messages), 2)
        self.assertEqual(self.msg.messages[0].text, 'one')
        self.assertEqual(self.msg.messages[1].text, 'two')


    def test_proto_fill_from_dict__map(self):
        ut.proto_fill_from_dict(self.msg, {'list_number32': map(int, [1,2,3])})
        self.assertEqual(self.msg.list_number32, [1,2,3])

    def test_proto_fill_from_dict__dict_map(self):
        ut.proto_fill_from_dict(self.msg, {'messages': map(dict, [{'text': 'one'}, {'text': 'two'}])})
        self.assertEqual(len(self.msg.messages), 2)
        self.assertEqual(self.msg.messages[0].text, 'one')
        self.assertEqual(self.msg.messages[1].text, 'two')

    def test_proto_fill_from_dict__filter(self):
        ut.proto_fill_from_dict(self.msg, {'list_number32': filter(lambda x: True, [1,2,3])})
        self.assertEqual(self.msg.list_number32, [1,2,3])

    def test_proto_fill_from_dict__dict_filter(self):
        ut.proto_fill_from_dict(self.msg, {'messages': filter(lambda x: True, [{'text': 'one'}, {'text': 'two'}])})
        self.assertEqual(len(self.msg.messages), 2)
        self.assertEqual(self.msg.messages[0].text, 'one')
        self.assertEqual(self.msg.messages[1].text, 'two')
