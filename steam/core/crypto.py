import sys
from struct import pack
from base64 import b64decode
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from Crypto.Hash import HMAC, SHA

public_key = """
MIGdMA0GCSqGSIb3DQEBAQUAA4GLADCBhwKBgQDf7BrWLBBmLBc1OhSwfFkRf53T
2Ct64+AVzRkeRuh7h3SiGEYxqQMUeYKO6UWiSRKpI2hzic9pobFhRr3Bvr/WARvY
gdTckPv+T1JzZsuVcNfFjrocejN1oWI0Rrtgt4Bo+hOneoo3S57G9F1fOpn5nsQ6
6WOiu4gZKODnFMBCiQIBEQ==
"""

BS = AES.block_size
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
    session_key = Random.new().read(32)
    cipher = PKCS1_OAEP.new(RSA.importKey(b64decode(public_key)))
    encrypted_session_key = cipher.encrypt(session_key + hmac_secret)
    return (session_key, encrypted_session_key)

def symmetric_encrypt(message, key):
    iv = Random.new().read(BS)
    return symmetric_encrypt_with_iv(message, key, iv)

def symmetric_encrypt_HMAC(message, key, hmac_secret):
    random_bytes = Random.new().read(3)

    hmac = HMAC.new(hmac_secret, digestmod=SHA)
    hmac.update(random_bytes)
    hmac.update(message)

    iv = hmac.digest()[:13] + random_bytes

    return symmetric_encrypt_with_iv(message, key, iv)

def symmetric_encrypt_with_iv(message, key, iv):
    encrypted_iv = AES.new(key, AES.MODE_ECB).encrypt(iv)
    cyphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message))
    return encrypted_iv + cyphertext

def symmetric_decrypt(cyphertext, key):
    iv = symmetric_decrypt_iv(cyphertext, key)
    return symmetric_decrypt_with_iv(cyphertext, key, iv)

def symmetric_decrypt_HMAC(cyphertext, key, hmac_secret):
    """:raises: :class:`RuntimeError` when HMAC verification fails"""
    iv = symmetric_decrypt_iv(cyphertext, key)
    message = symmetric_decrypt_with_iv(cyphertext, key, iv)

    hmac = HMAC.new(hmac_secret, digestmod=SHA)
    hmac.update(iv[-3:])
    hmac.update(message)

    if iv[:13] != hmac.digest()[:13]:
        raise RuntimeError("Unable to decrypt message. HMAC does not match.")

    return message

def symmetric_decrypt_iv(cyphertext, key):
    return AES.new(key, AES.MODE_ECB).decrypt(cyphertext[:BS])

def symmetric_decrypt_with_iv(cyphertext, key, iv):
    message = AES.new(key, AES.MODE_CBC, iv).decrypt(cyphertext[BS:])
    return unpad(message)
