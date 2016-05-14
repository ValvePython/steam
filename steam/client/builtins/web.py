"""
Web related features
"""
from binascii import hexlify
from steam import WebAPI
from steam.core.crypto import generate_session_key, symmetric_encrypt, sha1_hash, random_bytes
from steam.util.web import make_requests_session


class Web(object):
    def __init__(self, *args, **kwargs):
        super(Web, self).__init__(*args, **kwargs)

    def get_web_session_cookies(self):
        """Get web authentication cookies via WebAPI's ``AuthenticateUser``

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
            'encrypted_loginkey': symmetric_encrypt(self.webapi_authenticate_user_nonce, skey),
        }

        try:
            api = WebAPI(None)
            resp = api.ISteamUserAuth.AuthenticateUser(**data)
        except Exception as exp:
            self._logger.debug("get_web_session_cookies error: %s" % str(exp))
            return None

        return {
            'sessionid': hexlify(sha1_hash(random_bytes(32))),
            'steamLogin': resp['authenticateuser']['token'],
            'steamLoginSecure': resp['authenticateuser']['tokensecure'],
        }

    def get_web_session(self, language='english'):
        """Get a :class:`requests.Session` that is ready for use

        See :meth:`get_web_session_cookies`

        .. note::
            Auth cookies will only be send to ``(help|store).steampowered.com`` and ``steamcommunity.com`` domains

        :param language: localization language for steam pages
        :type language: :class:`str`
        :return: authenticated Session ready for use
        :rtype: :class:`requests.Session`, :class:`None`
        """
        cookies = self.get_web_session_cookies()
        if cookies is None:
            return None

        session = make_requests_session()

        for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
            for name, val in cookies.items():
                secure = (name == 'steamLoginSecure')
                session.cookies.set(name, val, domain=domain, secure=secure)

            session.cookies.set('Steam_Language', language, domain=domain)
            session.cookies.set('birthtime', '-3333', domain=domain)

        return session
