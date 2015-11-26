from base64 import b64decode
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA

public_key = """
MIGdMA0GCSqGSIb3DQEBAQUAA4GLADCBhwKBgQDf7BrWLBBmLBc1OhSwfFkRf53T
2Ct64+AVzRkeRuh7h3SiGEYxqQMUeYKO6UWiSRKpI2hzic9pobFhRr3Bvr/WARvY
gdTckPv+T1JzZsuVcNfFjrocejN1oWI0Rrtgt4Bo+hOneoo3S57G9F1fOpn5nsQ6
6WOiu4gZKODnFMBCiQIBEQ==
"""

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


def generate_session_key():
    session_key = Random.new().read(32)
    cipher = PKCS1_OAEP.new(RSA.importKey(b64decode(public_key)))
    encrypted_session_key = cipher.encrypt(session_key)
    return (session_key, encrypted_session_key)


def encrypt(message, key):
    iv = Random.new().read(BS)
    encrypted_iv = AES.new(key, AES.MODE_ECB).encrypt(iv)
    cyphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message))
    return encrypted_iv + cyphertext


def decrypt(cyphertext, key):
    iv = AES.new(key, AES.MODE_ECB).decrypt(cyphertext[:BS])
    message = AES.new(key, AES.MODE_CBC, iv).decrypt(cyphertext[BS:])
    return unpad(message)
