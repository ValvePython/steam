# -*- coding: utf-8 -*-
"""
This module simplifies the process of obtaining an authenticated session for steam websites.
After authentication is complete, a :class:`requests.Session` is created containing the auth cookies.
The session can be used to access ``steamcommunity.com``, ``store.steampowered.com``, and ``help.steampowered.com``.

Example usage:

.. code:: python

    import steam.webauth as wa

    user = wa.WebAuth('username', 'password')

    try:
        user.login()
    except wa.CaptchaRequired:
        print user.captcha_url
        # ask a human to solve captcha
        user.login(captcha='ABC123')
    except wa.EmailCodeRequired:
        user.login(email_code='ZXC123')
    except wa.TwoFactorCodeRequired:
        user.login(twofactor_code='ZXC123')

    wa.session.get('https://store.steampowered.com/account/history/')

Alternatively, if Steam Guard is not enabled on the account:

.. code:: python

    try:
        session = wa.WebAuth('username', 'password').login()
    except wa.HTTPError:
        pass

.. note::
    If you are using :class:`steam.client.SteamClient`, see :meth:`steam.client.builtins.web.Web.get_web_session()`

"""
from time import time
import sys
from base64 import b64encode
import requests

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from steam.core.crypto import backend

from steam.util.web import make_requests_session
from steam import SteamID

if sys.version_info < (3,):
    intBase = long
else:
    intBase = int


class WebAuth(object):
    key = None
    complete = False  #: whether authentication has been completed successfully
    session = None    #: :class:`requests.Session` (with auth cookies after auth is complete)
    captcha_gid = -1
    steamid = None    #: :class:`steam.steamid.SteamID` (after auth is complete)

    def __init__(self, username, password):
        self.__dict__.update(locals())
        self.session = make_requests_session()

    @property
    def captcha_url(self):
        """If a captch is required this property will return url to the image, or ``None``"""
        if self.captcha_gid == -1:
            return None
        else:
            return "https://store.steampowered.com/login/rendercaptcha/?gid=%s" % self.captcha_gid

    def get_rsa_key(self, username):
        """Get rsa key for a given username

        :param username: username
        :type username: :class:`str`
        :return: json response
        :rtype: :class:`dict`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        """
        try:
            resp = self.session.post('https://store.steampowered.com/login/getrsakey/',
                                    timeout=15,
                                    data={
                                        'username': username,
                                        'donotchache': int(time() * 1000),
                                        },
                                    ).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        return resp

    def _load_key(self):
        if not self.key:
            resp = self.get_rsa_key(self.username)

            nums = RSAPublicNumbers(intBase(resp['publickey_exp'], 16),
                                    intBase(resp['publickey_mod'], 16),
                                    )

            self.key = backend.load_rsa_public_numbers(nums)
            self.timestamp = resp['timestamp']

    def login(self, captcha='', email_code='', twofactor_code='', language='english'):
        """Attempts web login and returns on a session with cookies set

        :param captcha: text reponse for captcha challenge
        :type captcha: :class:`str`
        :param email_code: email code for steam guard
        :type email_code: :class:`str`
        :param twofactor_code: 2FA code for steam guard
        :type twofactor_code: :class:`str`
        :param language: select language for steam web pages (sets language cookie)
        :type language: :class:`str`
        :return: a session on success and :class:`None` otherwise
        :rtype: :class:`requests.Session`, :class:`None`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        :raises CaptchaRequired: when captcha is needed
        :raises EmailCodeRequired: when email is needed
        :raises TwoFactorCodeRequired: when 2FA is needed
        :raises LoginIncorrect: wrong username or password
        """
        if self.complete:
            return self.session

        self._load_key()

        data = {
            'username' : self.username,
            "password": b64encode(self.key.encrypt(self.password.encode('ascii'), PKCS1v15())),
            "emailauth": email_code,
            "emailsteamid": str(self.steamid) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": False,
            "donotcache": int(time() * 100000),
        }

        try:
            resp = self.session.post('https://store.steampowered.com/login/dologin/', data=data, timeout=15).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        self.captcha_gid = -1

        if resp['success'] and resp['login_complete']:
            self.complete = True
            self.password = None

            self.session.cookies.clear()
            data = resp['transfer_parameters']

            self.steamid = SteamID(data['steamid'])

            for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                self.session.cookies.set('steamLogin', '%s||%s' % (data['steamid'], data['token']),
                                    domain=domain, secure=False)
                self.session.cookies.set('steamLoginSecure', '%s||%s' % (data['steamid'], data['token_secure']),
                                    domain=domain, secure=True)
                self.session.cookies.set('Steam_Language', language, domain=domain)
                self.session.cookies.set('birthtime', '-3333', domain=domain)

            return self.session
        else:
            if resp.get('captcha_needed', False):
                self.captcha_gid = resp['captcha_gid']

                raise CaptchaRequired(resp['message'])
            elif resp.get('emailauth_needed', False):
                self.steamid = SteamID(resp['emailsteamid'])
                raise EmailCodeRequired(resp['message'])
            elif resp.get('requires_twofactor', False):
                raise TwoFactorCodeRequired(resp['message'])
            else:
                raise LoginIncorrect(resp['message'])

        return None


class WebAuthException(Exception):
    pass

class HTTPError(WebAuthException):
    pass

class LoginIncorrect(WebAuthException):
    pass

class CaptchaRequired(WebAuthException):
    pass

class EmailCodeRequired(WebAuthException):
    pass

class TwoFactorCodeRequired(WebAuthException):
    pass
