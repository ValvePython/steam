import unittest
import mock

from steam import guard as g

class TCguard(unittest.TestCase):
    def test_generate_twofactor_code_for_time(self):
        code = g.generate_twofactor_code_for_time(b'superdupersecret', timestamp=3000030)
        self.assertEqual(code, 'YRGQJ')

        code = g.generate_twofactor_code_for_time(b'superdupersecret', timestamp=3000029)
        self.assertEqual(code, '94R9D')

    def test_generate_confirmation_key(self):
        key = g.generate_confirmation_key(b'itsmemario', '', 100000)
        self.assertEqual(key, b'\xed\xb5\xe5\xad\x8f\xf1\x99\x01\xc8-w\xd6\xb5 p\xccz\xd7\xd1\x05')

        key = g.generate_confirmation_key(b'itsmemario', 'allow', 100000)
        self.assertEqual(key, b"Q'\x06\x80\xe1g\xa8m$\xb2hV\xe6g\x8b'\x8f\xf1L\xb0")
