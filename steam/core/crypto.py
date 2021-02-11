"""
All function in this module take and return :class:`bytes`
"""
import hashlib
import sys
from base64 import b64decode
from os import urandom as random_bytes
from struct import pack

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.hmac import HMAC
from cryptography.hazmat.primitives.serialization import load_der_public_key


class UniverseKey(object):
    """Public keys for Universes"""

    Public = load_der_public_key(b64decode("""
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
    encrypted_session_key = UniverseKey.Public.encrypt(
        session_key + hmac_secret,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA1()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return (session_key, encrypted_session_key)

def symmetric_encrypt(message, key):
    iv = random_bytes(BS)
    return symmetric_encrypt_with_iv(message, key, iv)

def symmetric_encrypt_ecb(message, key):
    padder = PKCS7(algorithms.AES.block_size).padder()
    plaintext = padder.update(message)
    plaintext += padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    cyphertext = encryptor.update(plaintext)
    cyphertext += encryptor.finalize()
    return cyphertext

def symmetric_encrypt_HMAC(message, key, hmac_secret):
    prefix = random_bytes(3)
    hmac = hmac_sha1(hmac_secret, prefix + message)
    iv = hmac[:13] + prefix
    return symmetric_encrypt_with_iv(message, key, iv)

def symmetric_encrypt_iv(iv, key):
    encryptor = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    cyphertext = encryptor.update(iv)
    cyphertext += encryptor.finalize()
    return cyphertext

def symmetric_encrypt_with_iv(message, key, iv):
    encrypted_iv = symmetric_encrypt_iv(iv, key)
    padder = PKCS7(algorithms.AES.block_size).padder()
    plaintext = padder.update(message)
    plaintext += padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    cyphertext = encryptor.update(plaintext)
    cyphertext += encryptor.finalize()
    return encrypted_iv + cyphertext

def symmetric_decrypt(cyphertext, key):
    iv = symmetric_decrypt_iv(cyphertext, key)
    return symmetric_decrypt_with_iv(cyphertext, key, iv)

def symmetric_decrypt_ecb(cyphertext, key):
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    plaintext = decryptor.update(cyphertext)
    plaintext += decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(plaintext)
    message += unpadder.finalize()
    return message

def symmetric_decrypt_HMAC(cyphertext, key, hmac_secret):
    """:raises: :class:`RuntimeError` when HMAC verification fails"""
    iv = symmetric_decrypt_iv(cyphertext, key)
    message = symmetric_decrypt_with_iv(cyphertext, key, iv)

    hmac = hmac_sha1(hmac_secret, iv[-3:] + message)

    if iv[:13] != hmac[:13]:
        raise RuntimeError("Unable to decrypt message. HMAC does not match.")

    return message

def symmetric_decrypt_iv(cyphertext, key):
    decryptor = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    iv = decryptor.update(cyphertext[:BS])
    iv += decryptor.finalize()
    return iv

def symmetric_decrypt_with_iv(cyphertext, key, iv):
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    plaintext = decryptor.update(cyphertext[BS:])
    plaintext += decryptor.finalize()
    unpadder = PKCS7(algorithms.AES.block_size).unpadder()
    message = unpadder.update(plaintext)
    message += unpadder.finalize()
    return message

def hmac_sha1(secret, data):
    h = HMAC(secret, hashes.SHA1())
    h.update(data)
    return h.finalize()

def sha1_hash(data):
    return hashlib.sha1(data).digest()

def rsa_publickey(mod, exp):
    return rsa.RSAPublicNumbers(e=exp, n=mod).public_key()

def pkcs1v15_encrypt(key, message):
    key.encrypt(
        message,
        padding.PKCS1v15,
    )
