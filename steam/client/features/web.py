"""
Web related features
"""
from Crypto.Hash import SHA
from Crypto.Random import new as randombytes
from steam import WebAPI
from steam.core.crypto import generate_session_key, symmetric_encrypt
from steam.util.web import make_requests_session


class Web(object):
    def __init__(self):
        super(Web, self).__init__()

    def get_web_session_cookies(self):
        """
        Get web authentication cookies via WebAPI's ``AuthenticateUser``

        .. note::
            only valid during the current steam session

        :return: dict with authentication cookies
        :rtype: :class:`dict`, :class:`None`
        """
        if not self.logged_on:
            return None

        skey, ekey = generate_session_key()

        data = {
            'steamid': self.steam_id,
            'sessionkey': ekey,
            'encrypted_loginkey': symmetric_encrypt(self.cm.webapi_authenticate_user_nonce, skey),
        }

        try:
            api = WebAPI(None)
            resp = api.ISteamUserAuth.AuthenticateUser(**data)
        except Exception as exp:
            self._logger.debug("get_web_session_cookies error: %s" % str(exp))
            return None

        return {
            'sessionid': SHA.new(randombytes().read(32)).hexdigest(),
            'steamLogin': resp['authenticateuser']['token'],
            'steamLoginSecure': resp['authenticateuser']['tokensecure'],
        }

    def get_web_session(self):
        """
        See :meth:`get_web_session_cookies`

        .. warning::
            Exercise caution when using the session.
            Auth cookies will be send with every request,
            regardless of the domain or https/http.

        :return: authenticated session ready for use
        :rtype: :class:`requests.Session`, :class:`None`
        """
        cookies = self.get_web_session_cookies()
        if cookies is None:
            return None

        session = make_requests_session()

        for name, val in cookies.items():
            session.cookies.set(name, val)

        return session
