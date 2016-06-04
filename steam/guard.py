import struct
from binascii import hexlify
from time import time
from steam import webapi
from steam.core.crypto import hmac_sha1, sha1_hash

def generate_twofactor_code(shared_secret):
    """Generate Steam 2FA code for login with current time

    :param shared_secret: authenticator shared shared_secret
    :type shared_secret: bytes
    :return: steam two factor code
    :rtype: str
    """
    return generate_twofactor_code_for_time(shared_secret, time() + get_time_offset())

def generate_twofactor_code_for_time(shared_secret, timestamp):
    """Generate Steam 2FA code for timestamp

    :param shared_secret: authenticator shared secret
    :type shared_secret: bytes
    :param timestamp: timestamp to use, if left out uses current time
    :type timestamp: int
    :return: steam two factor code
    :rtype: str
    """
    hmac = hmac_sha1(bytes(shared_secret),
                     struct.pack('>Q', int(timestamp)//30))  # this will NOT stop working in 2038

    start = ord(hmac[19:20]) & 0xF
    codeint = struct.unpack('>I', hmac[start:start+4])[0] & 0x7fffffff

    charset = '23456789BCDFGHJKMNPQRTVWXY'
    code = ''

    for _ in range(5):
        codeint, i = divmod(codeint, len(charset))
        code += charset[i]

    return code

def generate_confirmation_key(identity_secret, timestamp, tag=''):
    """Generate confirmation key for trades. Can only be used once.

    :param identity_secret: authenticator identity secret
    :type identity_secret: bytes
    :param timestamp: timestamp to use for generating key
    :type timestamp: int
    :param tag: tag identifies what the request, see list below
    :type tag: str
    :return: confirmation key
    :rtype: bytes

    Tag choices:

        * ``conf`` to load the confirmations page
        * ``details`` to load details about a trade
        * ``allow`` to confirm a trade
        * ``cancel`` to cancel a trade

    """
    data = struct.pack('>Q', int(timestamp)) + tag.encode('ascii') # this will NOT stop working in 2038
    return hmac_sha1(bytes(identity_secret), data)

def get_time_offset():
    """Get time offset from steam server time via WebAPI

    :return: time offset
    :rtype: int
    """
    try:
        resp = webapi.post('ITwoFactorService', 'QueryTime', 1, params={'http_timeout': 5})
    except:
        return 0

    ts = int(time())
    return int(resp.get('response', {}).get('server_time', ts)) - ts

def generate_device_id(steamid):
    """Generate Android device id

    :param steamid: Steam ID
    :type steamid: :class:`.SteamID`, :class:`int`
    :return: android device id
    :rtype: str
    """
    h = hexlify(sha1(str(steamid).encode('ascii'))).decode('ascii')
    return "android:%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:32])
