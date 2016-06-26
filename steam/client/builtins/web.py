"""
Web related features
"""
from steam import webapi
from steam.core.msg import MsgProto
from steam.enums.emsg import EMsg
from steam.core.crypto import generate_session_key, symmetric_encrypt
from steam.util.web import make_requests_session


class Web(object):
    def __init__(self, *args, **kwargs):
        super(Web, self).__init__(*args, **kwargs)

    def get_web_session_cookies(self):
        """Get web authentication cookies via WebAPI's ``AuthenticateUser``

        .. note::
            A session is only valid during the current steam session.

        :return: dict with authentication cookies
        :rtype: :class:`dict`, :class:`None`
        """
        if not self.logged_on: return None

        resp = self.send_job_and_wait(MsgProto(EMsg.ClientRequestWebAPIAuthenticateUserNonce), timeout=5)

        if resp is None: return None

        skey, ekey = generate_session_key()

        data = {
            'steamid': self.steam_id,
            'sessionkey': ekey,
            'encrypted_loginkey': symmetric_encrypt(resp.webapi_authenticate_user_nonce.encode('ascii'), skey),
        }

        try:
            resp = webapi.post('ISteamUserAuth', 'AuthenticateUser', 1, params=data)
        except Exception as exp:
            self._logger.debug("get_web_session_cookies error: %s" % str(exp))
            return None

        return {
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
