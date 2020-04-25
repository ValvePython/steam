import requests
from binascii import hexlify
from steam.core.crypto import sha1_hash, random_bytes

def make_requests_session():
    """
    :returns: requests session
    :rtype: :class:`requests.Session`
    """
    session = requests.Session()

    version = __import__('steam').__version__
    ua = "python-steam/{0} {1}".format(version,
                                session.headers['User-Agent'])
    session.headers['User-Agent'] = ua

    return session

def generate_session_id():
    """
    :returns: session id
    :rtype: :class:`str`
    """
    return hexlify(sha1_hash(random_bytes(32)))[:32].decode('ascii')
