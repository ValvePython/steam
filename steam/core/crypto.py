import sys
from os import urandom as random_bytes
from struct import pack
from base64 import b64decode
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.hashes import Hash, SHA1
from cryptography.hazmat.primitives.asymmetric.padding import PSS, OAEP, MGF1
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC, ECB
import cryptography.hazmat.backends
backend = cryptography.hazmat.backends.default_backend()


class UniverseKey(object):
    Public = backend.load_der_public_key(b64decode("""
MIGdMA0GCSqGSIb3DQEBAQUAA4GLADCBhwKBgQDf7BrWLBBmLBc1OhSwfFkRf53T
2Ct64+AVzRkeRuh7h3SiGEYxqQMUeYKO6UWiSRKpI2hzic9pobFhRr3Bvr/WARvY
gdTckPv+T1JzZsuVcNfFjrocejN1oWI0Rrtgt4Bo+hOneoo3S57G9F1fOpn5nsQ6
6WOiu4gZKODnFMBCiQIBEQ==
"""))

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * pack('B', BS - len(s) % BS)

if sys.version_info < (3,):
    unpad = lambda s: s[0:-ord(s[-1])]
else:
    unpad = lambda s: s[0:-s[-1]]


def generate_session_key(hmac_secret=b''):
    """
    :param hmac_secret: optional HMAC
    :type hmac_secret: :class:`bytes`
    :return: (session_key, encrypted_session_key) tuple
    :rtype: :class:`tuple`
    """
    session_key = random_bytes(32)
    encrypted_session_key = UniverseKey.Public.encrypt(session_key + hmac_secret,
                                                       OAEP(MGF1(SHA1()), SHA1(), None)
                                                       )
    return (session_key, encrypted_session_key)

def symmetric_encrypt(message, key):
    iv = random_bytes(BS)
    return symmetric_encrypt_with_iv(message, key, iv)

def symmetric_encrypt_HMAC(message, key, hmac_secret):
    prefix = random_bytes(3)

    hmac = HMAC(hmac_secret, SHA1(), backend)
    hmac.update(prefix)
    hmac.update(message)

    iv = hmac.finalize()[:13] + prefix

    return symmetric_encrypt_with_iv(message, key, iv)

def symmetric_encrypt_iv(iv, key):
    encryptor =  Cipher(AES(key), ECB(), backend).encryptor()
    return encryptor.update(iv) + encryptor.finalize()

def symmetric_encrypt_with_iv(message, key, iv):
    encrypted_iv = symmetric_encrypt_iv(iv, key)
    encryptor =  Cipher(AES(key), CBC(iv), backend).encryptor()
    cyphertext = encryptor.update(pad(message)) + encryptor.finalize()
    return encrypted_iv + cyphertext

def symmetric_decrypt(cyphertext, key):
    iv = symmetric_decrypt_iv(cyphertext, key)
    return symmetric_decrypt_with_iv(cyphertext, key, iv)

def symmetric_decrypt_HMAC(cyphertext, key, hmac_secret):
    """:raises: :class:`RuntimeError` when HMAC verification fails"""
    iv = symmetric_decrypt_iv(cyphertext, key)
    message = symmetric_decrypt_with_iv(cyphertext, key, iv)

    hmac = HMAC(hmac_secret, SHA1(), backend)
    hmac.update(iv[-3:])
    hmac.update(message)

    if iv[:13] != hmac.finalize()[:13]:
        raise RuntimeError("Unable to decrypt message. HMAC does not match.")

    return message

def symmetric_decrypt_iv(cyphertext, key):
    decryptor =  Cipher(AES(key), ECB(), backend).decryptor()
    return decryptor.update(cyphertext[:BS]) + decryptor.finalize()

def symmetric_decrypt_with_iv(cyphertext, key, iv):
    decryptor =  Cipher(AES(key), CBC(iv), backend).decryptor()
    return unpad(decryptor.update(cyphertext[BS:]) + decryptor.finalize())

def sha1_hash(data):
    sha = Hash(SHA1(), backend)
    sha.update(data)
    return sha.finalize()
