import unittest
import mock
from binascii import hexlify

from steam.core import crypto


class crypto_testcase(unittest.TestCase):
    def setUp(self):
#         patcher = mock.patch('os.urandom')
#         self.addCleanup(patcher.stop)
#         self.urandom = patcher.start()
#         self.urandom.side_effect = lambda n: b'1' * n

        patcher = mock.patch('steam.core.crypto.random_bytes')
        self.addCleanup(patcher.stop)
        self.random_bytes = patcher.start()
        self.random_bytes.side_effect = lambda n: b'1' * n

#     def test_keygen(self):
#         expected_key = b'1' * 32
#         expected_ekey = (b'82a5d4d6de38e443ed3e6f0a1701a2c47bc98e0860e7883638ea5263a1744d02'
#                          b'f733f09bc6b0f9b2a371bbb79b639208521f88658aab38c23e181d39a58ae39e'
#                          b'c4e207fba822d523028d3c04e812abdc2247aa8d8e6e4a89c7a65671c5bcb329'
#                          b'51c6d721ccf57cc2920d6ff3b69bfb2c611b1275badcd3e37fe024c9a25bf4b0'
#                          )
# 
#         key, ekey = crypto.generate_session_key()
#         ekey = hexlify(ekey)
# 
#         self.assertEqual(key, expected_key)
#         self.assertEqual(ekey, expected_ekey)
# 
#     def test_keygen_with_challenge(self):
#         expected_key = b'1' * 32
#         expected_ekey = (b'd710c55122f9bf772ec9c0f21d75c05055764d5445902577340029b4707e1725'
#                          b'd61bec77f41b17faed6577d08c812cef76dca8b0b0b2329e1f33ea4cfa31f1e6'
#                          b'0babc859c55b6ac94497b5dc9b0bc89629290dc038274af4377771e088e92887'
#                          b'30d3906f6b698fd113ba36e3d28a5e1ce0283b27a1adda538df5dc5b179cf84f'
#                          )
# 
#         key, ekey = crypto.generate_session_key(b'5'*16)
#         ekey = hexlify(ekey)
# 
#         self.assertEqual(key, expected_key)
#         self.assertEqual(ekey, expected_ekey)

    def test_encryption_legacy(self):
        message = b'My secret message'
        key = b'9' * 32

        cyphertext = crypto.symmetric_encrypt(message, key)
        dmessage = crypto.symmetric_decrypt(cyphertext, key)

        self.assertEqual(message, dmessage)

    def test_encryption_hmac(self):
        message = b'My secret message'
        key = b'9' * 32
        hmac = b'3' * 16

        cyphertext = crypto.symmetric_encrypt_HMAC(message, key, hmac)
        dmessage = crypto.symmetric_decrypt_HMAC(cyphertext, key, hmac)

        self.assertEqual(message, dmessage)

        # failing HMAC check
        with self.assertRaises(RuntimeError):
            crypto.symmetric_decrypt_HMAC(cyphertext, key, b'4'*16)

    def test_sha1_hash(self):
        self.assertEqual(crypto.sha1_hash(b'123'),    b'@\xbd\x00\x15c\x08_\xc3Qe2\x9e\xa1\xff\\^\xcb\xdb\xbe\xef')
        self.assertEqual(crypto.sha1_hash(b'999999'), b'\x1fU#\xa8\xf55(\x9b4\x01\xb2\x99X\xd0\x1b)f\xeda\xd2')
