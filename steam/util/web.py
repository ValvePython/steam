import requests
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()


def make_requests_session():
    """
    :returns: gevent cooperative requests session
    :rtype: :class:`requests.Session`
    """
    session = requests.Session()

    # use urllib3 to make requests gevent cooperative
    session.mount('any', requests.adapters.HTTPAdapter())

    version = __import__('steam').__version__
    ua = "python-steam/{0} {1}".format(version,
                                session.headers['User-Agent'])
    session.headers['User-Agent'] = ua

    return session
