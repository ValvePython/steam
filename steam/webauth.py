# -*- coding: utf-8 -*-
"""
This module simplifies the process of obtaining an authenticated session for steam websites.
After authentication is complete, a :class:`requests.Session` is created containing the auth cookies.
The session can be used to access ``steamcommunity.com``, ``store.steampowered.com``, and ``help.steampowered.com``.

.. warning::
    A web session may expire randomly, or when you login from different IP address.
    Some pages will return status code `401` when that happens.
    Keep in mind if you are trying to write robust code.

.. note::
    If you are using :class:`.SteamClient` take a look at :meth:`.get_web_session()`

.. note::
    If you need to authenticate as a mobile device for things like trading confirmations
    use :class:`MobileWebAuth` instead. The login process is identical, and in addition
    you will get :attr:`.oauth_token`.


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

    user.session.get('https://store.steampowered.com/account/history/')
    # OR
    session = user.login()
    session.get('https://store.steampowered.com/account/history')

Alternatively, if Steam Guard is not enabled on the account:

.. code:: python

    try:
        session = wa.WebAuth('username', 'password').login()
    except wa.HTTPError:
        pass

The :class:`WebAuth` instance should be discarded once a session is obtained
as it is not reusable.
"""
import sys
import json
from time import time
from base64 import b64encode
import requests

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from steam.core.crypto import backend

from steam import SteamID, webapi
from steam.util.web import make_requests_session, generate_session_id

if sys.version_info < (3,):
    intBase = long
else:
    intBase = int


class WebAuth(object):
    key = None
    complete = False    #: whether authentication has been completed successfully
    session = None      #: :class:`requests.Session` (with auth cookies after auth is complete)
    session_id = None   #: :class:`str`, session id string
    captcha_gid = -1
    steam_id = None     #: :class:`.SteamID` (after auth is complete)

    def __init__(self, username, password):
        self.__dict__.update(locals())
        self.session = make_requests_session()
        self._session_setup()

    def _session_setup(self):
        pass

    @property
    def captcha_url(self):
        """If a captch is required this property will return url to the image, or ``None``"""
        if self.captcha_gid == -1:
            return None
        else:
            return "https://steamcommunity.com/login/rendercaptcha/?gid=%s" % self.captcha_gid

    def get_rsa_key(self, username):
        """Get rsa key for a given username

        :param username: username
        :type username: :class:`str`
        :return: json response
        :rtype: :class:`dict`
        :raises HTTPError: any problem with http request, timeouts, 5xx, 4xx etc
        """
        try:
            resp = self.session.post('https://steamcommunity.com/login/getrsakey/',
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

    def _send_login(self, captcha='', email_code='', twofactor_code=''):
        data = {
            'username' : self.username,
            "password": b64encode(self.key.encrypt(self.password.encode('ascii'), PKCS1v15())),
            "emailauth": email_code,
            "emailsteamid": str(self.steam_id) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": 'true',
            "donotcache": int(time() * 100000),
        }

        try:
            return self.session.post('https://steamcommunity.com/login/dologin/', data=data, timeout=15).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

    def _finalize_login(self, login_response):
        self.steam_id = SteamID(login_response['transfer_parameters']['steamid'])

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
        resp = self._send_login(captcha=captcha, email_code=email_code, twofactor_code=twofactor_code)

        self.captcha_gid = -1

        if resp['success'] and resp['login_complete']:
            self.complete = True
            self.password = None

            for cookie in list(self.session.cookies):
                for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                    self.session.cookies.set(cookie.name, cookie.value, domain=domain, secure=cookie.secure)

            self.session_id = generate_session_id()

            for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                self.session.cookies.set('Steam_Language', language, domain=domain)
                self.session.cookies.set('birthtime', '-3333', domain=domain)
                self.session.cookies.set('sessionid', self.session_id, domain=domain)

            self._finalize_login(resp)

            return self.session
        else:
            if resp.get('captcha_needed', False):
                self.captcha_gid = resp['captcha_gid']

                raise CaptchaRequired(resp['message'])
            elif resp.get('emailauth_needed', False):
                self.steam_id = SteamID(resp['emailsteamid'])
                raise EmailCodeRequired(resp['message'])
            elif resp.get('requires_twofactor', False):
                raise TwoFactorCodeRequired(resp['message'])
            else:
                raise LoginIncorrect(resp['message'])

        return None


class MobileWebAuth(WebAuth):
    """Identical to :class:`WebAuth`, except it authenticates as a mobile device."""
    oauth_token = None  #: holds oauth_token after successful login

    def _send_login(self, captcha='', email_code='', twofactor_code=''):
        data = {
            'username' : self.username,
            "password": b64encode(self.key.encrypt(self.password.encode('ascii'), PKCS1v15())),
            "emailauth": email_code,
            "emailsteamid": str(self.steam_id) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": 'true',
            "donotcache": int(time() * 100000),
            "oauth_client_id": "DE45CD61",
            "oauth_scope": "read_profile write_profile read_client write_client",
        }

        self.session.cookies.set('mobileClientVersion', '0 (2.1.3)')
        self.session.cookies.set('mobileClient', 'android')

        try:
            return self.session.post('https://steamcommunity.com/login/dologin/', data=data, timeout=15).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))
        finally:
            self.session.cookies.pop('mobileClientVersion', None)
            self.session.cookies.pop('mobileClient', None)

    def _finalize_login(self, login_response):
        data = json.loads(login_response['oauth'])
        self.steam_id = SteamID(data['steamid'])
        self.oauth_token = data['oauth_token']


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
