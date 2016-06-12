"""
This module is used to safely store account credentials and provide mobile authenticator codes.

Example usage:

.. code:: python

    import steam.account

    account = steam.account.SteamAccount('username', 'password')
    account.set_account_property('identity_secret', 'XYZ')
    account.set_account_property('shared_secret', 'XYZ')
    code    = account.login_code
    key     = account.get_confirmation_key('conf')



TODO:
    - Where to save the credentials (Windows/Linux)?
    - Implement mobile authenticator features?
"""
import os
import sys
import json
import base64
import re

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from steam.guard import *
import steam.webauth

if sys.platform.startswith('win'):
    BASE_LOCATION = '.' #Windows
else:
    BASE_LOCATION = '.'

DEFAULT_MOBILE_HEADERS = {
    'X-Requested-With': 'com.valvesoftware.android.steam.community',
    'User-agent': 'Mozilla/5.0 (Linux; U; Android 4.1.1; en-us; Google Nexus 4 - 4.1.1 - API 16 - 768x1280 Build/JRO03S) \
     AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
}

ACCOUNT_ATTRIBUTES = ['username', 'password', 'steamid', 'shared_secret', 'identity_secret', 'revocation_code',\
                      'secret_1', 'serial_number', 'deviceid', 'oauth_token']

class SteamAccount(object):
    username            = None
    password            = None
    _path               = None
    _file               = None
    _fernet_key         = None
    _fernet_suite       = None
    _web_auth           = None
    _session            = None

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self._setup()

    def __del__(self):
        try:
            self._update_credential_file()
        except TypeError:
            """
            Ignore TypeError exception when destructor gets called after the memory has been cleared
            """
            pass
        self._file.close()

    def set_account_property(self, property, value):
        setattr(self, property, value)
        self._update_credential_file()

    @property
    def login_code(self):
        try:
            return generate_twofactor_code(self.shared_secret)
        except AttributeError:
            raise SharedSecretNotSet('Add shared_secret to this instance to generate login codes')

    def get_confirmation_key(self, tag, timestamp=None):
        if not timestamp:
            timestamp = get_time_offset()
        try:
            return generate_confirmation_key(self.identity_secret, timestamp, tag)
        except AttributeError:
            raise IdentitySecretNotSet('Add identity_secret to this instance to generate confirmation keys')

    def fetch_mobile_confirmations(self, retries=1):
        self._verify_mobile_session()

        if not self._verify_mobile_authenticator():
            raise MobileAuthenticatorException('The steam mobile authenticator is required to access the mobile confirmations.')

        timestamp = get_time_offset()
        confirmation_key = self.get_confirmation_key('conf', timestamp)

        confirmation_uri = 'https://steamcommunity.com/mobileconf/conf?p=%s&a=%s&k=%s&t=%s&m=android&tag=conf' %\
              ( self.deviceid, self.steamid, confirmation_key, timestamp)

        response = self.session.get(confirmation_uri, headers=DEFAULT_MOBILE_HEADERS)

        raw_confirmations = [ ]

        if response.status_code == 200:
            if 'Invalid authenticator' in response.text:
                retries += 1
                return self.fetch_mobile_confirmations(retries)

            confirmation_ids = re.findall(r'data-confid="(\d+)"', response.text)
            confirmation_keys = re.findall(r'data-key="(\d+)"', response.text)
            confirmation_descriptions = re.findall(r'<div>((Confirm|Trade with|Sell -) .+)<\/div>', response.text)

            if confirmation_ids and confirmation_keys:
                for index, confirmation_id in enumerate(confirmation_ids):
                    raw_confirmations.append({
                        'id': confirmation_id,
                        'key': confirmation_keys[index],
                        'description': confirmation_descriptions[index]
                    })
                return raw_confirmations
        return [ ]

    def add_mobile_authenticator(self):
        if self._verify_mobile_authenticator():
            raise MobileAuthenticatorException('The steam mobile authenticator is already enabled.')

        self._verify_mobile_session()

        deviceid = getattr(self, 'deviceid') or generate_device_id(self.steamid)

        data = {
            'steamid':              self.steamid,
            'sms_phone_id':         1,
            'access_token':         self.oauth_token,
            'authenticator_time':   get_time_offset(),
            'authenticator_type':   1,
            'device_identifier':    deviceid
        }

        response = self.session.post('https://api.steampowered.com/ITwoFactorService/AddAuthenticator/v1/',
                                     data, headers=DEFAULT_MOBILE_HEADERS)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            if response_json.get('response').get('status') == 1:
                self.set_account_property('shared_secret',      response_json.get('response').get('shared_secret'))
                self.set_account_property('identity_secret',    response_json.get('response').get('identity_secret'))
                self.set_account_property('revocation_code',    response_json.get('response').get('revocation_code'))
                self.set_account_property('secret_1',           response_json.get('response').get('secret_1'))
                self.set_account_property('serial_number',      response_json.get('response').get('serial_number'))
                self.set_account_property('deviceid',           deviceid)
                return True
        return False

    def finalize_mobile_authenticator(self, sms_code, retries=1):
        if self._verify_mobile_authenticator():
            raise MobileAuthenticatorException('The steam mobile authenticator is already enabled.')

        self._verify_mobile_session()

        if not sms_code:
            raise SMSCodeNotProvided('The sms code is required for finalizing the process of adding the mobile\
             authenticator')

        timestamp = get_time_offset()

        data = {
            'steamid':              self.steamid,
            'access_token':         self.oauth_token,
            'authenticator_time':   timestamp,
            'authenticator_code':   generate_twofactor_code_for_time(self.shared_secret, timestamp),
            'activation_code':      sms_code
        }

        response = self.session.post('https://api.steampowered.com/ITwoFactorService/FinalizeAddAuthenticator/v1/',
                                     data, headers=DEFAULT_MOBILE_HEADERS)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            if response_json.get('response').get('success'):
                self.set_account_property('has_mobile_authenticator', True)
                return True
            else:
                if response_json.get('response').get('success') and retries < 30:
                    retries += 1
                    return self._finalize_mobile_authenticator(sms_code, retries)
        return False

    def remove_mobile_authenticator(self):
        if not self._verify_mobile_authenticator():
            raise MobileAuthenticatorException('The steam mobile authenticator is not enabled.')

        self._verify_mobile_session()

        data = {
            'steamid':              self.steamid,
            'steamguard_scheme':    2,
            'revocation_code':      self.revocation_code,
            'access_token':         self.oauth_token
        }

        response = self.session.post('https://api.steampowered.com/ITwoFactorService/RemoveAuthenticator/v1/',
                                     data, headers=DEFAULT_MOBILE_HEADERS)

        if response.status_code == 200:
            response_json = json.loads(response.text)
            if response_json.get('response').get('success'):
                self.set_account_property('has_mobile_authenticator', False)
                return True
        return False

    def _verify_mobile_session(self):
        if not isinstance(self._web_auth, steam.webauth.MobileWebAuth):
            raise MobileAuthenticatorException('A mobile session is required.')

        if self._web_auth.complete:
            raise MobileAuthenticatorException('The mobile session has to be logged in to steam.')

    def _verify_mobile_authenticator(self):
        if getattr(self, 'has_mobile_authenticator') and self.has_mobile_authenticator:
            return True
        return False

    def _setup(self):
        self._generate_fernet_key()
        self._spawn_fernet_suite()
        self._path = '%s/%s' % (BASE_LOCATION, self.username)
        self._file = open(self._path, 'r+')
        if not os.path.isfile(self._path):
            self._create_credential_file()
        else:
            credentials = self._parse_credential_file()
            for key, value in credentials.iteritems():
                setattr(self, key, value)

    def _create_credential_file(self):
        data = json.dumps({
            'username': self.username,
            'password': self.password
        })
        text = self._fernet_suite.encrypt(data)
        self._file.write(text)

    def _parse_credential_file(self):

        text = self._file.read()
        data = json.loads(self._fernet_suite.decrypt(text))
        return data

    def _update_credential_file(self):
        credentials = self._gather_credentials()
        data = json.dumps(credentials)

        text = self._fernet_suite.encrypt(data)
        self._file.truncate()
        self._file.write(text)

    def _gather_credentials(self):
        data = { }
        names = dir(self)
        for name in names:
            if name in ACCOUNT_ATTRIBUTES:
                data.__setitem__(name, getattr(self, name))
        return data

    def _generate_fernet_key(self):
        digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        digest.update(bytes(self.password))
        self._fernet_key = base64.urlsafe_b64encode(digest.finalize())

    def _spawn_fernet_suite(self):
        self._fernet_suite = Fernet(self._fernet_key)

    def _spawn_web_session(self):
        self._web_auth = steam.webauth.WebAuth(self.username, self.password)

    def _spawn_mobile_session(self):
        self._web_auth = steam.webauth.MobileWebAuth(self.username, self.password)

    def _login_web_session(self, captcha='', email_code='', twofactor_code=''):
        try:
            self._web_auth.login()

        except steam.webauth.CaptchaRequired:
            if not captcha:
                raise CaptchaNotProvided('The steam login captcha is required for logging in, but was not provided.')
            self._web_auth.login(captcha=captcha)

        except steam.webauth.EmailCodeRequired:
            if not email_code:
                raise EMailCodeNotProvided('The email code is required for logging in, but was not provided.')
            self._web_auth.login(email_code=email_code)

        except steam.webauth.TwoFactorCodeRequired:
            if not twofactor_code:
                try:
                    twofactor_code = self.login_code
                except SharedSecretNotSet:
                    raise TwoFACodeNotProvided('The twofactor code is required for logging in, but was not provided.')
            self._web_auth.login(twofactor_code=twofactor_code)

        if self._web_auth.complete:
            if not getattr(self, 'steamid'):
                self.set_account_property('steamid', self._web_auth.steamid)

            if isinstance(self._web_auth, steam.webauth.MobileWebAuth) and not getattr(self, 'oauth_token'):
                self.set_account_property('oauth_token', self._web_auth.oauth_token)

            self._session = self._web_auth.session
        else:
            raise WebAuthNotComplete('The web authentication could not be completed.')

class SteamAccountException(Exception):
    pass

class SharedSecretNotSet(SteamAccountException):
    pass

class IdentitySecretNotSet(SteamAccountException):
    pass

class WebAuthNotComplete(SteamAccountException):
    pass

class MobileAuthenticatorException(SteamAccountException):
    pass

class ParameterNotProvidedException(SteamAccountException):
    pass

class CaptchaNotProvided(ParameterNotProvidedException):
    pass

class EMailCodeNotProvided(ParameterNotProvidedException):
    pass

class TwoFACodeNotProvided(ParameterNotProvidedException):
    pass

class SMSCodeNotProvided(ParameterNotProvidedException):
    pass