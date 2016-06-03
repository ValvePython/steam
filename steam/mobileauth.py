# -*- coding: utf-8 -*-
"""
This module simplifies the process of obtaining an authenticated session for mobile steam websites.
After authentication is complete, a :class:`requests.Session` is created containing the auth and mobile specific cookies.
The session can be used to access ``steamcommunity.com``, ``store.steampowered.com``, and ``help.steampowered.com``.
The main purpose of a mobile session, is to access the mobile trade confirmations page and to easily access the
ITwoFactorService api, but can also used to access all 'normal' steam pages.


.. warning::
    A web session may expire randomly, or when you login from different IP address.
    Some pages will return status code `401` when that happens.
    Keep in mind if you are trying to write robust code.

Example usage:

.. code:: python

    import steam.mobileauth as ma

    user = ma.WebAuth('username', 'password')

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

The :class:`MobileAuth` instance should be discarded once a session is obtained
as it is not reusable.
"""
import json
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


class MobileAuth(object):
    key = None
    complete = False  #: whether authentication has been completed successfully
    session = None  #: :class:`requests.Session` (with auth cookies after auth is complete)
    captcha_gid = -1
    steamid = None  #: :class:`steam.steamid.SteamID` (after auth is complete)
    oauth = {}

    def __init__(self, username, password):
        self.__dict__.update(locals())
        self.session = make_requests_session()

    @property
    def captcha_url(self):
        if self.captcha_gid == -1:
            return None
        else:
            return "https://store.steampowered.com/login/rendercaptcha/?gid=%s" % self.captcha_gid

    def get_rsa_key(self, username):
        try:
            resp = self.session.post('https://steamcommunity.com/mobilelogin/getrsakey/',
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
        if self.complete:
            return self.session

        for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
            self.session.cookies.set('forceMobile', '1', domain=domain, secure=False)
            self.session.cookies.set('mobileClientVersion', '0 (2.1.3)', domain=domain, secure=False)
            self.session.cookies.set('mobileClient', 'android', domain=domain, secure=False)
            self.session.cookies.set('Steam_Language', 'english', domain=domain, secure=False)
            self.session.cookies.set('dob', '', domain=domain, secure=False)

        self._load_key()

        data = {
            'username': self.username,
            "password": b64encode(self.key.encrypt(self.password.encode('ascii'), PKCS1v15())),
            "emailauth": email_code,
            "emailsteamid": str(self.steamid) if email_code else '',
            "twofactorcode": twofactor_code,
            "captchagid": self.captcha_gid,
            "captcha_text": captcha,
            "loginfriendlyname": "python-steam webauth",
            "rsatimestamp": self.timestamp,
            "remember_login": 'true',
            "donotcache": int(time() * 100000),
        }
        data['oauth_client_id'] = 'DE45CD61'
        data['oauth_scope'] = 'read_profile write_profile read_client write_client'
        data['loginfriendlyname'] = '#login_emailauth_friendlyname_mobile'

        try:
            resp = self.session.post('https://steamcommunity.com/mobilelogin/dologin/', data=data, timeout=15).json()
        except requests.exceptions.RequestException as e:
            raise HTTPError(str(e))

        self.captcha_gid = -1

        if resp['success'] and resp['login_complete']:
            self.complete = True
            self.password = None
            resp['oauth'] = json.loads(resp['oauth'])
            self.steamid = SteamID(resp['oauth']['steamid'])
            self.oauth = resp['oauth']
            for domain in ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']:
                self.session.cookies.set('steamLogin', '%s||%s' % (self.steamid, resp['oauth']['wgtoken']),
                                         domain=domain, secure=False)
                self.session.cookies.set('steamLoginSecure', '%s||%s' % (self.steamid, resp['oauth']['wgtoken_secure']),
                                         domain=domain, secure=True)

            return resp
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


class MobileWebAuthException(Exception):
    pass


class HTTPError(MobileWebAuthException):
    pass


class LoginIncorrect(MobileWebAuthException):
    pass


class CaptchaRequired(MobileWebAuthException):
    pass


class EmailCodeRequired(MobileWebAuthException):
    pass


class TwoFactorCodeRequired(MobileWebAuthException):
    pass
